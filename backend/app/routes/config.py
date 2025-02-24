from fastapi import APIRouter, HTTPException, FastAPI, status
from opcua import ua
from app.config import settings  # Assumed to provide OPCUA_URL and NAMESPACE_URI
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
from app.models.config import ConfigRequest, ConfigResponse
from typing import Dict

# Initialize logger and router
logger = get_logger(__name__)
router = APIRouter()

# Initialize OPC UA client with settings
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

# API Routes
@router.get("", response_model=ConfigResponse)
async def get_config():
    """Retrieve the current configuration from the OPC UA server."""
    if not opcua_client.client:
        logger.error("OPC UA client is not connected.")
        raise HTTPException(status_code=503, detail="OPC UA client is not connected.")
    try:
        logger.info("Attempting to retrieve configuration from OPC UA server.")
        config = await opcua_client.get_config()
        logger.info(f"Retrieved config: {config}")
        return ConfigResponse(status="success", config=config)
    except ua.UaStatusCodeError as e:
        logger.error(f"OPC UA error retrieving config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OPC UA error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error retrieving config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("", response_model=ConfigResponse)
async def add_config(request: ConfigRequest):
    """Add or update a namespace and its variables on the OPC UA server."""
    if not opcua_client.client:
        logger.error("OPC UA client is not connected.")
        raise HTTPException(status_code=503, detail="OPC UA client is not connected.")
    try:
        await opcua_client.add_namespace_and_variables(request.namespace_uri, request.variables)
        logger.info(f"Added/updated namespace {request.namespace_uri} with variables: {request.variables}")
        return ConfigResponse(status="success", config=request.variables)
    except Exception as e:
        logger.error(f"Error adding configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, str | bool])
async def health_check():
    """Check the health of the OPC UA connection."""
    try:
        if not opcua_client.client:
            return {
                "status": "unhealthy",
                "opcua_connected": False,
                "message": "OPC UA client is not initialized."
            }
        # Test connection by fetching namespace index
        await opcua_client.get_namespace_index()
        return {
            "status": "healthy",
            "opcua_connected": True,
            "message": "OPC UA client is connected and operational."
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "opcua_connected": False,
            "message": str(e)
        }

# FastAPI Application Setup
app = FastAPI(title="OPC UA Config API")

@app.on_event("startup")
async def startup_event():
    """Connect to the OPC UA server on application startup."""
    try:
        await opcua_client.connect()
        logger.info("OPC UA client connected during startup.")
    except Exception as e:
        logger.error(f"Failed to connect OPC UA client on startup: {str(e)}")
        # Don't raise here; let health check reflect the failure
        opcua_client.client = None

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from the OPC UA server on application shutdown."""
    if opcua_client.client:
        try:
            await opcua_client.disconnect()
            logger.info("OPC UA client disconnected during shutdown.")
        except Exception as e:
            logger.error(f"Failed to disconnect OPC UA client on shutdown: {str(e)}")

# Mount the router with a prefix
app.include_router(router, prefix="/config", tags=["config"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)