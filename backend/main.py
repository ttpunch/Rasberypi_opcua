from fastapi import FastAPI, HTTPException
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

@app.on_event("startup")
async def startup_event():
    try:
        await opcua_client.connect()
        logger.info("Successfully connected to OPCUA server")
    except Exception as e:
        logger.error(f"Failed to connect to OPCUA server: {e}")
        # Don't raise here, let the application start even if OPCUA server is not available
        # Individual routes will handle connection errors

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