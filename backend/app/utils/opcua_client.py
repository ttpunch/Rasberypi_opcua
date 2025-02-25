from asyncua import Client, ua
from .logger import get_logger

logger = get_logger(__name__)

class OPCUAClient:
    def __init__(self, url: str, namespace_uri: str):
        self.url = url
        self.client = None
        self.namespace_uri = namespace_uri

    async def connect(self):
        """Establish connection to the OPCUA server."""
        try:
            logger.info(f"Connecting to OPCUA server at {self.url}")
            self.client = Client(url=self.url)
            # Connect anonymously by not setting any user credentials
            await self.client.connect()
            logger.info(f"Connected to OPCUA server at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to OPCUA server: {str(e)}")
            self.client = None  # Ensure client is reset on failure
            raise

    async def disconnect(self):
        """Disconnect from the OPCUA server."""
        try:
            await self.client.disconnect()
            logger.info("Disconnected from OPCUA server")
        except Exception as e:
            logger.error(f"Error disconnecting from OPCUA server: {str(e)}")

    async def get_namespace_index(self):
        """Get the index of the namespace."""
        try:
            return await self.client.get_namespace_index(self.namespace_uri)
        except Exception as e:
            logger.error(f"Error getting namespace index: {str(e)}")
            raise

    async def get_objects_node(self):
        """Get the objects node from the OPCUA server."""
        try:
            return self.client.get_objects_node()
        except Exception as e:
            logger.error(f"Error getting objects node: {str(e)}")
            raise

    async def write_value(self, node_id: str, value: any):
        """Write a value to a specific node in the OPCUA server."""
        try:
            node = self.client.get_node(node_id)
            await node.set_value(value)
            logger.info(f"Wrote value {value} to node {node_id}")
        except Exception as e:
            logger.error(f"Error writing value to {node_id}: {str(e)}")
            raise

    async def read_value(self, node_id: str):
        """Read a value from a specific node in the OPCUA server."""
        try:
            node = self.client.get_node(node_id)
            value = await node.get_value()
            logger.info(f"Read value {value} from node {node_id}")
            return value
        except Exception as e:
            logger.error(f"Error reading value from {node_id}: {str(e)}")
            raise

    async def add_namespace_and_variables(self, namespace_uri: str, variables: dict):
        """Add a namespace and its variables to the OPCUA server."""
        try:
            namespace_idx = await self.get_namespace_index()
            objects = await self.get_objects_node()
            logger.info(f"Namespace index: {namespace_idx}")
            logger.info(f"Objects node: {objects}")
            # Await the creation of the object
            myobj = await objects.add_object(namespace_idx, "MyObject")
            logger.info(f"Created object: {myobj}")

            logger.info(f"Variables: {variables}")
            for var_name, initial_value in variables.items():
                logger.debug(f"Processing variable: {var_name} with value {initial_value}")

                # Await the addition of the variable
                node = await myobj.add_variable(namespace_idx, var_name, initial_value)
                logger.debug(f"Added variable node: {node}")

                # Set the variable to be writable
                await node.set_writable(True)
                logger.info(f"Added variable {var_name} with value {initial_value}")
        except Exception as e:
            logger.error(f"Error adding namespace and variables: {str(e)}")
            raise

    async def get_config(self):
        """Retrieve current namespace and variable configurations."""
        try:
            namespace_idx = await self.get_namespace_index()
            myobj = await self.get_objects_node().get_child([f"{namespace_idx}:MyObject"])
            config = {}
            for node in await myobj.get_children():
                name = node.get_browse_name().Name
                value = await node.get_value()
                config[name] = value
            logger.info(f"Retrieved config: {config}")
            return config
        except Exception as e:
            logger.error(f"Error retrieving config: {str(e)}")
            raise

    async def create_subscription(self, interval: int, callback):
        """Create a subscription for real-time updates."""
        try:
            subscription = await self.client.create_subscription(interval, callback)
            logger.info("Created OPCUA subscription")
            return subscription
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise