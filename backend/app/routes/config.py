from fastapi import APIRouter, HTTPException, FastAPI, status, Depends
from asyncua import ua
from app.config import settings
from app.utils.opcua_client import OPCUAClient
from app.utils.logger import get_logger
from app.models.config import ConfigRequest, ConfigResponse, NamespaceConfig, VariableConfig
from typing import Union, Dict, Any, Optional
from pydantic import BaseModel
from asyncua.common.node import Node
import json
from pathlib import Path

# Initialize logger and router
logger = get_logger(__name__)
router = APIRouter()

# Standard health check response model
class HealthCheckResponse(BaseModel):
    status: str
    opcua_connected: bool
    message: str

# Initialize OPC UA client with settings
opcua_client = OPCUAClient(settings.OPCUA_URL, settings.NAMESPACE_URI)

# Dependency to get OPC UA client and handle connection
async def get_connected_client() -> OPCUAClient:
    """Ensure OPC UA client is connected before processing request."""
    if opcua_client.client is None:
        try:
            await opcua_client.connect()
        except Exception as e:
            logger.error(f"Failed to connect to OPC UA server: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPC UA client is not connected."
            )
    return opcua_client

# API Routes
@router.get("", response_model=ConfigResponse)
async def get_config(client: OPCUAClient = Depends(get_connected_client)):
    """Retrieve the current configuration from the OPC UA server."""
    try:
        logger.info("Attempting to retrieve configuration from OPC UA server.")
        
        # Read directly from variables_store.json
        variables_file = Path("/Users/vinod/Library/Mobile Documents/com~apple~CloudDocs/Coding/Rasberypi_opcua/opcua_server/variables_store.json")
        if variables_file.exists():
            with open(variables_file, 'r') as f:
                stored_variables = json.load(f)
                logger.info(f"Retrieved variables from store: {stored_variables}")
                return ConfigResponse(status="success", config=stored_variables)
        else:
            return ConfigResponse(status="success", config={})
            
    except Exception as e:
        logger.error(f"Error retrieving configuration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
# Add this at the top level with other constants
VARIABLES_STORE_PATH = Path("/Users/vinod/Library/Mobile Documents/com~apple~CloudDocs/Coding/Rasberypi_opcua/opcua_server/variables_store.json")

# Update the add_config function
@router.post("", response_model=ConfigResponse)
async def add_config(request: ConfigRequest, client: OPCUAClient = Depends(get_connected_client)):
    """Add or update a namespace and its variables on the OPC UA server."""
    try:
        logger.info(f"Received config request: namespace_uri={request.namespace_uri}, variables={request.variables}")
        
        if not request.namespace_uri:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="namespace_uri cannot be empty"
            )
        
        if not isinstance(request.variables, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="variables must be a dictionary"
            )
        
        # Update OPC UA server
        await client.add_namespace_and_variables(request.namespace_uri, request.variables)
        
        # Update variables_store.json
        try:
            # Read existing variables
            if VARIABLES_STORE_PATH.exists():
                with open(VARIABLES_STORE_PATH, 'r') as f:
                    stored_variables = json.load(f)
            else:
                stored_variables = {}
            
            # Update with new variables
            stored_variables.update(request.variables)
            
            # Write back to file
            with open(VARIABLES_STORE_PATH, 'w') as f:
                json.dump(stored_variables, f)
            
            logger.info(f"Updated variables store with: {request.variables}")
        except Exception as e:
            logger.error(f"Error updating variables store: {str(e)}")
            # Continue execution even if file operation fails
        
        return ConfigResponse(status="success", config=request.variables)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding configuration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/namespaces", response_model=Dict[str, Any])
async def get_namespaces(client: OPCUAClient = Depends(get_connected_client)):
    """Get all available namespaces on the server."""
    try:
        namespaces = await client.client.get_namespace_array()
        return {"namespaces": namespaces}
    except Exception as e:
        logger.error(f"Error getting namespaces: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of the OPC UA connection."""
    try:
        if opcua_client.client is None:
            try:
                # Attempt to connect if not connected
                await opcua_client.connect()
                # Test connection by fetching namespace index
                await opcua_client.get_namespace_index()
                return HealthCheckResponse(
                    status="healthy",
                    opcua_connected=True,
                    message="OPC UA client is connected and operational."
                )
            except Exception as e:
                logger.error(f"Failed to connect during health check: {str(e)}")
                return HealthCheckResponse(
                    status="unhealthy",
                    opcua_connected=False,
                    message=f"OPC UA connection failed: {str(e)}"
                )
        else:
            # Test existing connection
            await opcua_client.get_namespace_index()
            return HealthCheckResponse(
                status="healthy",
                opcua_connected=True,
                message="OPC UA client is connected and operational."
            )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            opcua_connected=False,
            message=str(e)
        )

# FastAPI Application Setup
app = FastAPI(
    title="OPC UA Config API",
    description="API for configuring OPC UA server variables",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Connect to the OPC UA server on application startup."""
    try:
        await opcua_client.connect()
        logger.info("OPC UA client connected during startup.")
    except Exception as e:
        logger.error(f"Failed to connect OPC UA client on startup: {str(e)}")
        # Don't raise here; let health check reflect the failure

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from the OPC UA server on application shutdown."""
    if opcua_client.client:
        try:
            await opcua_client.disconnect()
            logger.info("OPC UA client disconnected during shutdown.")
        except Exception as e:
            logger.error(f"Failed to disconnect OPC UA client on shutdown: {str(e)}")

# Add route for explicit debug validation check
@app.post("/validation_check", status_code=status.HTTP_200_OK)
async def validation_check(request: ConfigRequest):
    """Debug endpoint to validate request format without processing."""
    return {
        "message": "Request validation passed",
        "request_data": {
            "namespace_uri": request.namespace_uri,
            "variables": request.variables
        }
    }

# Mount the router with a prefix
app.include_router(router, prefix="/config", tags=["config"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)