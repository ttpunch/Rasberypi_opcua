# fastapi_opcua.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import asyncio
from asyncua import Client
from asyncua.ua import MessageSecurityMode
import uvicorn
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for client and target node
opcua_client = None
target_object_node = None
sub = None  # Global subscription object

class SubHandler:
    """Subscription Handler for receiving events from server"""
    def datachange_notification(self, node, val, data):
        logger.info(f"New data change event {node} {val}")

    def event_notification(self, event):
        logger.info(f"New event {event}")

# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    global opcua_client, target_object_node, sub
    try:
        # Initialize client with security settings
        opcua_client = Client("opc.tcp://localhost:4841/freeopcua/server/")
        # Set up security policy for username/password authentication
        opcua_client.set_security_string("Basic256Sha256,SignAndEncrypt,admin,admin123")
        opcua_client.secure_channel_timeout = 10000
        # Set user credentials
        opcua_client.set_user("admin")
        opcua_client.set_password("admin123")
        await opcua_client.connect()

        # Get namespace index and "MyObject" node
        idx = await opcua_client.get_namespace_index("http://examples.freeopcua.github.io")
        target_object_node = await opcua_client.nodes.root.get_child(f"Objects/{idx}:MyObject")
        
        # Set up subscription handler
        handler = SubHandler()
        sub = await opcua_client.create_subscription(500, handler)
        
        # Subscribe to MyVariable
        myvar = await target_object_node.get_child(f"{idx}:MyVariable")
        await sub.subscribe_data_change(myvar)
        
        # Subscribe to events
        await sub.subscribe_events()
        
        logger.info("Connected to OPC UA server and subscriptions set up")
    except Exception as e:
        logger.error(f"Failed to connect to OPC UA server: {str(e)}")
        raise

    yield

    # Shutdown
    if sub:
        await sub.delete()
    if opcua_client:
        await opcua_client.disconnect()
        logger.info("Disconnected from OPC UA server")

app = FastAPI(lifespan=lifespan)

@app.post("/add_variable/")
async def add_variable(name: str, value: int):
    if not opcua_client or not target_object_node:
        raise HTTPException(status_code=500, detail="OPC UA client not initialized")

    try:
        idx = await opcua_client.get_namespace_index("http://examples.freeopcua.github.io")
        new_var = await target_object_node.add_variable(idx, name, value)
        await new_var.set_writable()
        logger.info(f"Added variable '{name}' with value {value}")
        return {"message": f"Variable '{name}' added with value {value}"}
    except Exception as e:
        logger.error(f"Failed to add variable '{name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add variable: {str(e)}")

@app.get("/read_variable/{name}")
async def read_variable(name: str):
    if not opcua_client or not target_object_node:
        raise HTTPException(status_code=500, detail="OPC UA client not initialized")

    try:
        idx = await opcua_client.get_namespace_index("http://examples.freeopcua.github.io")
        var_node = await target_object_node.get_child(f"{idx}:{name}")
        value = await var_node.read_value()
        logger.info(f"Read variable '{name}': {value}")
        return {"name": name, "value": value}
    except Exception as e:
        logger.error(f"Failed to read variable '{name}': {str(e)}")
        raise HTTPException(status_code=404, detail=f"Variable not found or error: {str(e)}")

@app.post("/call_method/{method_name}")
async def call_method(method_name: str, x: int, y: int):
    if not opcua_client or not target_object_node:
        raise HTTPException(status_code=500, detail="OPC UA client not initialized")

    try:
        idx = await opcua_client.get_namespace_index("http://examples.freeopcua.github.io")
        result = await target_object_node.call_method(f"{idx}:{method_name}", x, y)
        logger.info(f"Called method '{method_name}' with result: {result}")
        return {"method": method_name, "result": result}
    except Exception as e:
        logger.error(f"Failed to call method '{method_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Method call failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)