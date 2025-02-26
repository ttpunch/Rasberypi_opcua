from asyncua import ua
from config.namespaces import NAMESPACE_URI
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class ConfigHandler:
    def __init__(self):
        self.namespace_index = None
        self.objects_node = None
        self.server = None

    async def setup(self, server):
        """Set up the configuration handler with the server instance."""
        self.server = server  # Store the server reference
        self.namespace_index = await self.server.get_namespace_index(NAMESPACE_URI)
        self.objects_node = self.server.nodes.objects
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
            if namespace_uri != NAMESPACE_URI:
                namespace_index = await self.server.register_namespace(namespace_uri)
            else:
                namespace_index = self.namespace_index
            
            # Create or update an object node
            # First check if MyObject exists
            try:
                myobj = await self.objects_node.get_child([f"{namespace_index}:MyObject"])
                logger.info("Found existing MyObject")
            except ua.UaError:
                # Object doesn't exist, create it
                myobj = await self.objects_node.add_object(namespace_index, "MyObject")
                logger.info("Created new MyObject")
            
            # Add or update variables
            for var_name, initial_value in variables.items():
                try:
                    # Check if variable exists
                    var_node = await myobj.get_child([f"{namespace_index}:{var_name}"])
                    # Update existing variable
                    await var_node.write_value(initial_value)
                    logger.info(f"Updated variable {var_name} with value {initial_value}")
                except ua.UaError:
                    # Variable doesn't exist, create it
                    var_node = await myobj.add_variable(namespace_index, var_name, initial_value)
                    await var_node.set_writable()
                    logger.info(f"Added new variable {var_name} with value {initial_value}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding namespace and variables: {str(e)}")
            raise

    async def get_config(self):
        """Retrieve current namespace and variable configurations."""
        try:
            config = {}
            try:
                myobj = await self.objects_node.get_child([f"{self.namespace_index}:MyObject"])
                children = await myobj.get_children()
                
                for node in children:
                    browse_name = await node.read_browse_name()
                    name = browse_name.Name
                    value = await node.read_value()
                    config[name] = value
                    
                logger.info(f"Retrieved config: {config}")
                return config
            except ua.UaError as e:
                logger.warning(f"MyObject not found or empty: {str(e)}")
                return config
        except Exception as e:
            logger.error(f"Error getting config: {str(e)}")
            raise