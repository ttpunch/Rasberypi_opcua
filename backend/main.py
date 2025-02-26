from fastapi import FastAPI, HTTPException, WebSocket
import asyncio
import json
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from app.routes import data, config, websocket
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
from app.config import settings

app = FastAPI(title="OPCUA Backend API")
logger = get_logger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OPCUA client
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

# Include routers
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(websocket.router)

# Add these variables at the top level
connected_clients = set()
variables_file = Path("/Users/vinod/Library/Mobile Documents/com~apple~CloudDocs/Coding/Rasberypi_opcua/opcua_server/variables_store.json")

# Add these new functions
async def broadcast_variables():
    if not connected_clients:
        return
    
    try:
        with open(variables_file, 'r') as f:
            variables = json.load(f)
        
        for client in connected_clients:
            await client.send_json({"type": "variables_update", "data": variables})
    except Exception as e:
        logger.error(f"Error broadcasting variables: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
            # Send current variables
            with open(variables_file, 'r') as f:
                variables = json.load(f)
            await websocket.send_json({"type": "variables_update", "data": variables})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(websocket)

# Modify startup event
@app.on_event("startup")
async def startup_event():
    try:
        await opcua_client.connect()
        logger.info("Successfully connected to OPCUA server")
        
        # Start background task to monitor variables file
        asyncio.create_task(monitor_variables_file())
    except Exception as e:
        logger.error(f"Failed to connect to OPCUA server: {e}")

# Add file monitoring
async def monitor_variables_file():
    last_modified = None
    while True:
        try:
            current_modified = variables_file.stat().st_mtime
            if last_modified != current_modified:
                last_modified = current_modified
                await broadcast_variables()
        except Exception as e:
            logger.error(f"Error monitoring variables file: {e}")
        await asyncio.sleep(1)  # Check every second

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await opcua_client.disconnect()
        logger.info("Successfully disconnected from OPCUA server")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    try:
        connected = opcua_client.client.uaclient and opcua_client.client.uaclient._connection
        return {
            "status": "healthy",
            "opcua_connected": connected,
            "message": "OPCUA Backend Server"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "opcua_connected": False,
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)