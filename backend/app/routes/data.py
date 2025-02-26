from fastapi import APIRouter, HTTPException
from typing import Any
from app.config import settings
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

async def ensure_client_connected():
    """Ensure the OPCUA client is connected."""
    if not opcua_client.client or not opcua_client.client.uaclient:
        await opcua_client.connect()

@router.get("/", response_description="Retrieve real-time data from OPCUA server ")
async def get_data():
    try:
        await ensure_client_connected()  # Ensure client is connected
        namespace_idx = await opcua_client.get_namespace_index()
        objects_node = await opcua_client.get_objects_node()  # Await the coroutine
        
        # Check if MyObject exists
        try:
            myobj = await objects_node.get_child([f"{namespace_idx}:MyObject"])
        except Exception as e:
            logger.error(f"MyObject node not found: {str(e)}")
            raise HTTPException(status_code=404, detail="MyObject node not found")
        
        data = {}
        for node in await myobj.get_children():
            name = (await node.read_browse_name()).Name
            value = await node.read_value()
            data[name] = value
        logger.info(f"Retrieved data: {data}")
        return {"status": "success", "data": data}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {str(e)}")

@router.post("/", response_description="Update data on OPCUA server")
async def update_data(variable: str, value: Any):
    try:
        await ensure_client_connected()
        namespace_idx = await opcua_client.get_namespace_index()
        objects_node = await opcua_client.get_objects_node()
        
        try:
            myobj = await objects_node.get_child([f"{namespace_idx}:MyObject"])
            var_node = await myobj.get_child([f"{namespace_idx}:{variable}"])
            
            # Get current value to determine the correct type
            current_value = await var_node.read_value()
            
            # Convert the input value to match the node's data type
            try:
                converted_value = type(current_value)(value)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value type. Expected {type(current_value).__name__}, got {type(value).__name__}"
                )
            
            # Write the converted value
            await var_node.write_value(converted_value)
            logger.info(f"Updated {variable} to value: {converted_value}")
            return {"status": "success", "message": f"Updated {variable} successfully"}
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Node not found or access denied: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Node not found or access denied: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update data: {str(e)}")