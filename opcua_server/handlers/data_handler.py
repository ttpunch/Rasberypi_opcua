from asyncua import ua
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class DataHandler:
    def __init__(self):
        self.data = {}
        self.server = None
        
    async def setup(self, server):
        """Set up the data handler with the server instance."""
        self.server = server
        logger.info("Data handler initialized")

    async def update_variable(self, node_id, value):
        """Update a variable value in the OPCUA server."""
        try:
            node = self.server.get_node(node_id)
            await node.write_value(value)
            logger.info(f"Updated {node_id} to value: {value}")
        except Exception as e:
            logger.error(f"Error updating variable {node_id}: {str(e)}")
            raise

    async def get_variable(self, node_id):
        """Retrieve a variable value from the OPCUA server."""
        try:
            node = self.server.get_node(node_id)
            value = await node.read_value()
            logger.info(f"Retrieved value for {node_id}: {value}")
            return value
        except Exception as e:
            logger.error(f"Error getting variable {node_id}: {str(e)}")
            raise

    async def subscribe_to_variable(self, node_id, callback):
        """Subscribe to a variable for real-time updates."""
        try:
            # Create subscription handler
            handler = SubscriptionHandler(callback)
            
            # Create subscription
            subscription = await self.server.create_subscription(500, handler)
            
            # Subscribe to data changes for the given node
            node = self.server.get_node(node_id)
            handle = await subscription.subscribe_data_change(node)
            
            logger.info(f"Subscribed to {node_id} for updates")
            return subscription, handle
        except Exception as e:
            logger.error(f"Error subscribing to {node_id}: {str(e)}")
            raise
            
# Subscription handler class
class SubscriptionHandler:
    def __init__(self, callback):
        self.callback = callback
        
    async def datachange_notification(self, node, val, data):
        """Called when a subscribed variable's value changes."""
        try:
            # Execute the callback with the new value
            await self.callback(node, val)
        except Exception as e:
            logger.error(f"Error in subscription callback: {str(e)}")