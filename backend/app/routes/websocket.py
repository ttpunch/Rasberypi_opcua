from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState  # Import the correct WebSocketState
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
from app.config import settings
import asyncio
import json

router = APIRouter()
logger = get_logger(__name__)
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

class DataChangeHandler:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def datachange_notification(self, node, val, data):
        try:
            if self.websocket.application_state == WebSocketState.CONNECTED:
                browse_name = await node.read_browse_name()
                data_dict = {browse_name.Name: val}
                await self.websocket.send_text(json.dumps({"event": "update", "data": data_dict}))
                logger.info(f"Sent WebSocket update: {data_dict}")
            else:
                logger.warning("WebSocket is not connected. Skipping send.")
        except Exception as e:
            logger.error(f"Error in datachange_notification: {str(e)}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Ensure client is connected before proceeding
        if not opcua_client.client or not opcua_client.client.uaclient:
            try:
                # Get authentication parameters from settings
                await opcua_client.connect()
                logger.info("Successfully authenticated with OPC UA server")
            except Exception as auth_error:
                error_msg = str(auth_error)
                if "BadIdentityTokenRejected" in error_msg:
                    error_msg = "Invalid credentials or authentication failed"
                logger.error(f"Authentication failed: {error_msg}")
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "data": {
                        "message": "Authentication failed",
                        "details": error_msg
                    }
                }))
                await websocket.close(code=4001)  # Custom code for auth failure
                return
            
        namespace_idx = await opcua_client.get_namespace_index()
        objects_node = await opcua_client.get_objects_node()
        
        # Ensure MyObject exists
        try:
            myobj = await objects_node.get_child([f"{namespace_idx}:MyObject"])
        except Exception as e:
            logger.error(f"Failed to get MyObject: {str(e)}")
            await websocket.send_text(json.dumps({
                "event": "error",
                "data": {"message": "Failed to access OPC UA node"}
            }))
            await websocket.close(code=1011)  # Internal error
            return
        
        handler = DataChangeHandler(websocket)
        subscription = await opcua_client.create_subscription(500, handler)
        nodes = await myobj.get_children()
        
        # Subscribe to all child nodes
        for node in nodes:
            try:
                await subscription.subscribe_data_change(node)
                logger.info(f"Subscribed to node: {await node.read_browse_name()}")
            except Exception as sub_error:
                logger.error(f"Failed to subscribe to node: {str(sub_error)}")
        
        # Keep the connection alive
        while websocket.application_state == WebSocketState.CONNECTED:
            try:
                # Send heartbeat to check connection
                await websocket.send_text(json.dumps({"event": "heartbeat"}))
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Connection error: {str(e)}")
                break
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_text(json.dumps({
                "event": "error",
                "data": {"message": "Internal server error"}
            }))
            await websocket.close(code=1011)
        except:
            pass
    finally:
        if 'subscription' in locals():
            try:
                await subscription.delete()
                logger.info("Subscription deleted")
            except Exception as e:
                logger.error(f"Error deleting subscription: {str(e)}")