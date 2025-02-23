from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from asyncua import Client, ua
from app.config import settings
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
import asyncio
import json

router = APIRouter()
logger = get_logger(__name__)
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Ensure client is connected before proceeding
        if not opcua_client.client or not opcua_client.client.uaclient:
            # Connect anonymously
            await opcua_client.connect()
            
        namespace_idx = await opcua_client.get_namespace_index()
        objects_node = await opcua_client.get_objects_node()
        
        # First ensure MyObject exists
        try:
            myobj = await objects_node.get_child([f"{namespace_idx}:MyObject"])
        except Exception as e:
            # Create MyObject if it doesn't exist
            myobj = await objects_node.add_object(namespace_idx, "MyObject")
            logger.info("Created MyObject node")
        
        async def data_change_handler(node, val, data):
            try:
                browse_name = await node.read_browse_name()
                data_dict = {browse_name.Name: val.Value.Value}
                await websocket.send_text(json.dumps({"event": "update", "data": data_dict}))
                logger.info(f"Sent WebSocket update: {data_dict}")
            except Exception as e:
                logger.error(f"Error in data_change_handler: {str(e)}")
        
        subscription = await opcua_client.create_subscription(500, data_change_handler)
        nodes = await myobj.get_children()
        for node in nodes:
            await subscription.subscribe_data_change(node)
        
        while True:
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close(code=1001)
        except:
            pass
    finally:
        if 'subscription' in locals():
            await subscription.delete()