import asyncio
from asyncua import Server
from config.settings import SERVER_URL, NAMESPACE_URI, VARIABLES, SERVER_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class OPCUAServer:
    def __init__(self):
        self.server = Server()
        self.namespace = None
        
    async def setup(self):
        try:
            # Server setup
            await self.server.init()
            self.server.set_endpoint(SERVER_URL)
            self.server.set_server_name(SERVER_CONFIG["name"])
            
            # Register namespace
            self.namespace = await self.server.register_namespace(NAMESPACE_URI)
            logger.info(f"Namespace {NAMESPACE_URI} registered with index {self.namespace}")
            
            # Create object node
            objects = self.server.nodes.objects
            
            # Add variables
            for var_name, initial_value in VARIABLES.items():
                var = await objects.add_variable(self.namespace, var_name, initial_value)
                await var.set_writable()
                logger.info(f"Added variable {var_name} with value {initial_value}")
            
            # Start the server
            await self.server.start()
            logger.info(f"Server started at {SERVER_URL}")
            
        except Exception as e:
            logger.error(f"Error setting up OPCUA server: {str(e)}")
            raise
    
    async def stop(self):
        if self.server:
            await self.server.stop()
            logger.info("Server stopped")

async def main():
    server = OPCUAServer()
    try:
        logger.info(f"Starting OPCUA server at {SERVER_URL}")
        await server.setup()
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        logger.info("Stopping OPCUA server")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())