from opcua import ua
from config.namespaces import NAMESPACE_URI
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class ConfigHandler:
    def __init__(self):
        self.namespace_index = None
        self.objects_node = None

    async def setup(self, server):
        """Set up the configuration handler with the server instance."""
        self.namespace_index = server.get_namespace_index(NAMESPACE_URI)
        self.objects_node = server.get_objects_node()
        logger.info("Config handler initialized")

    async def add_namespace_and_variables(self, namespace_uri, variables):
        """
        Add a namespace and its variables to the OPCUA server.
        
        Args:
            namespace_uri (str): URI of the namespace.
            variables (dict): Dictionary of variable names and initial values.
        """
        try:
            # Register namespace if not already registered
            if self.namespace_index is None:
                self.namespace_index = await self.server.register_namespace(namespace_uri)
            
            # Create or update an object node
            myobj = self.objects_node.add_object(self.namespace_index, "MyObject")
            
            # Add or update variables
            for var_name, initial_value in variables.items():
                node = myobj.add_variable(self.namespace_index, var_name, initial_value)
                node.set_writable(True)
                logger.info(f"Added/updated variable {var_name} with value {initial_value}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding namespace and variables: {str(e)}")
            raise

    async def get_config(self):
        """Retrieve current namespace and variable configurations."""
        try:
            config = {}
            myobj = self.objects_node.get_child(["0:Objects", f"{self.namespace_index}:MyObject"])
            for node in myobj.get_children():
                name = node.get_browse_name().Name
                value = await node.get_value()
                config[name] = value
            logger.info(f"Retrieved config: {config}")
            return config
        except Exception as e:
            logger.error(f"Error getting config: {str(e)}")
            raise