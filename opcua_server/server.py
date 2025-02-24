import asyncio
import random
from asyncua import Server, ua
from config.settings import SERVER_URL, NAMESPACE_URI, VARIABLES, SERVER_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class OPCUAServer:
    def __init__(self):
        self.server = Server()
        self.namespace = None
        self.temperature_var = None

    async def setup(self):
        try:
            # Server setup
            await self.server.init()
            self.server.set_endpoint(SERVER_URL)
            self.server.set_server_name(SERVER_CONFIG["name"])

            # Allow anonymous access
            self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
            self.server.set_security_IDs(["Anonymous"])

            # Register namespace
            self.namespace = await self.server.register_namespace(NAMESPACE_URI)
            logger.info(f"Namespace {NAMESPACE_URI} registered with index {self.namespace}")

            # Create object node
            objects = self.server.nodes.objects

            # Check if MyObject exists, if not create it
            try:
                myobj = await objects.get_child([f"{self.namespace}:MyObject"])
                logger.info("MyObject node already exists")
            except Exception as e:
                myobj = await objects.add_object(self.namespace, "MyObject")
                logger.info("Created MyObject node")

            # Add variables to MyObject
            for var_name, initial_value in VARIABLES.items():
                var = await myobj.add_variable(self.namespace, var_name, initial_value)
                await var.set_writable()
                logger.info(f"Added variable {var_name} with value {initial_value}")

            # Add temperature variable to MyObject
            self.temperature_var = await myobj.add_variable(self.namespace, "Temperature", 20.0)
            await self.temperature_var.set_writable()
            logger.info("Added Temperature variable with initial value 20.0")

            # Start the server
            await self.server.start()
            logger.info(f"Server started at {SERVER_URL}")

            # Start updating the temperature variable
            asyncio.create_task(self.update_temperature())

        except Exception as e:
            logger.error(f"Error setting up OPCUA server: {str(e)}")
            raise

    async def update_temperature(self):
        while True:
            new_value = random.uniform(15.0, 25.0)
            await self.temperature_var.write_value(new_value)
            logger.info(f"Updated Temperature variable to {new_value}")
            await asyncio.sleep(1)

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