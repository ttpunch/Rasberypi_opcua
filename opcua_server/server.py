import asyncio
import random
from asyncua import Server, ua
from config.settings import SERVER_URL, NAMESPACE_URI, VARIABLES, SERVER_CONFIG
from utils.logger import get_logger
from asyncua.ua import SecurityPolicyType
import json
import os
from pathlib import Path

logger = get_logger(__name__)

# Add UserManager class
class MyUserManager:
    def __init__(self):
        self.user_db = {"admin": "admin123"}  # Username: Password database

    async def check_user_token(self, isession, username, password, user_token):
        if username in self.user_db and self.user_db[username] == password:
            return True
        return False

# Add this class at the top level, after the MyUserManager class
class SubHandler:
    """Subscription Handler for monitoring variable changes"""
    def datachange_notification(self, node, val, data):
        logger.info(f"Variable changed - Node: {node}, Value: {val}")

    def event_notification(self, event):
        logger.info(f"Event received: {event}")



class OPCUAServer:
    def __init__(self):
        self.server = Server()
        self.namespace = None
        self.subscription = None
        self.handler = None
        self.variables_file = Path("variables_store.json")
        self.stored_variables = self.load_variables()

    def load_variables(self):
        """Load variables from storage file"""
        if self.variables_file.exists():
            try:
                with open(self.variables_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading variables: {e}")
        return {}

    def save_variables(self, variables):
        """Save variables to storage file"""
        try:
            with open(self.variables_file, 'w') as f:
                json.dump(variables, f)
            logger.info("Variables saved to storage")
        except Exception as e:
            logger.error(f"Error saving variables: {e}")

    async def setup(self):
        try:
            # Server setup
            await self.server.init()
            self.server.set_endpoint(SERVER_URL)
            self.server.set_server_name(SERVER_CONFIG["name"])

            # Set up security policies and user authentication
            self.server.set_security_policy([
                SecurityPolicyType.NoSecurity,  # Allow unsecured connections for username/password
                SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                SecurityPolicyType.Basic256Sha256_Sign
            ])
            
            # Configure user authentication
            self.server.user_manager = MyUserManager()
            self.server.set_security_IDs(["Anonymous", "Username"])  # Support both anonymous and username auth

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

            # Load and add stored variables
            for var_name, initial_value in self.stored_variables.items():
                var = await myobj.add_variable(self.namespace, var_name, initial_value)
                await var.set_writable()
                logger.info(f"Restored variable {var_name} with value {initial_value}")

            # Add new variables to MyObject
            for var_name, initial_value in VARIABLES.items():
                if var_name not in self.stored_variables:
                    var = await myobj.add_variable(self.namespace, var_name, initial_value)
                    await var.set_writable()
                    logger.info(f"Added variable {var_name} with value {initial_value}")
                    self.stored_variables[var_name] = initial_value

            # Save the updated variables
            self.save_variables(self.stored_variables)

            # Set up monitoring with persistence
            self.handler = SubHandler()
            self.subscription = await self.server.create_subscription(
                period=500,
                handler=self.handler
            )

            # Subscribe to all variables
            for node in await myobj.get_children():
                await self.subscription.subscribe_data_change(node)
                logger.info(f"Monitoring variable: {await node.read_browse_name()}")

            # Start the server
            await self.server.start()
            logger.info(f"Server started at {SERVER_URL}")

        except Exception as e:
            logger.error(f"Error setting up OPCUA server: {str(e)}")
            raise


    async def stop(self):
        if self.subscription:
            await self.subscription.delete()
            logger.info("Subscription deleted")
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