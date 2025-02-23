import asyncio
from opcua import Client
from handlers.config_handler import ConfigHandler
from config.settings import SERVER_URL, NAMESPACE_URI
import pytest

@pytest.mark.asyncio
async def test_add_namespace_and_variables():
    """Test adding a namespace and variables to the OPCUA server."""
    client = Client(SERVER_URL)
    config_handler = ConfigHandler()
    try:
        await client.connect()
        variables = {"test_variable": 42}
        await config_handler.add_namespace_and_variables(NAMESPACE_URI, variables)
        
        # Verify the variable was added
        idx = await client.get_namespace_index(NAMESPACE_URI)
        node = client.get_node(f"ns={idx};s=MyObject.test_variable")
        value = await node.get_value()
        assert value == 42, "Variable value mismatch"
    except Exception as e:
        assert False, f"Config error: {str(e)}"
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_get_config():
    """Test retrieving the current configuration from the OPCUA server."""
    client = Client(SERVER_URL)
    config_handler = ConfigHandler()
    try:
        await client.connect()
        config = await config_handler.get_config()
        assert isinstance(config, dict), "Config should be a dictionary"
        assert "variable1" in config or "test_variable" in config, "Expected variables not found"
        print(f"Current config: {config}")
    except Exception as e:
        assert False, f"Get config error: {str(e)}"
    finally:
        await client.disconnect()