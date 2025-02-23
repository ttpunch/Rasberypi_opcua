from fastapi import APIRouter, HTTPException, Body
from opcua import Client, ua
from app.config import settings
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
from app.models.config import ConfigRequest, ConfigResponse

router = APIRouter()
logger = get_logger(__name__)
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

@router.post("", response_model=ConfigResponse)
async def add_config(request: ConfigRequest):
    try:
        await opcua_client.add_namespace_and_variables(request.namespace_uri, request.variables)
        logger.info(f"Added/updated namespace {request.namespace_uri} with variables: {request.variables}")
        return ConfigResponse(
            status="success",
            config=request.variables
        )
    except Exception as e:
        logger.error(f"Error adding configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ConfigResponse)
async def get_config():
    try:
        config = await opcua_client.get_config()
        logger.info(f"Retrieved config: {config}")
        return ConfigResponse(
            status="success",
            config=config
        )
    except Exception as e:
        logger.error(f"Error retrieving config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))