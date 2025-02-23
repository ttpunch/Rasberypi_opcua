from opcua import ua
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class DataHandler:
    def __init__(self):
        self.data = {}

    async def update_variable(self, node_id, value):
        """Update a variable value in the OPCUA server."""
        try:
            node = self.server.get_node(node_id)
            await node.set_value(value)
            logger.info(f"Updated {node_id} to value: {value}")
        except Exception as e:
            logger.error(f"Error updating variable {node_id}: {str(e)}")
            raise

    async def get_variable(self, node_id):
        """Retrieve a variable value from the OPCUA server."""
        try:
            node = self.server.get_node(node_id)
            value = await node.get_value()
            logger.info(f"Retrieved value for {node_id}: {value}")
            return value
        except Exception as e:
            logger.error(f"Error getting variable {node_id}: {str(e)}")
            raise

    async def subscribe_to_variable(self, node_id, callback):
        """Subscribe to a variable for real-time updates."""
        try:
            subscription = self.server.create_subscription(500, callback)  # Update every 500ms
            handle = subscription.subscribe_data_change(node_id)
            logger.info(f"Subscribed to {node_id} for updates")
            return subscription, handle
        except Exception as e:
            logger.error(f"Error subscribing to {node_id}: {str(e)}")
            raise