import asyncio
from opcua import Client
from server import OPCUAServer
from config.settings import SERVER_URL
import pytest

@pytest.mark.asyncio
async def test_opcua_server_starts():
    """Test if the OPCUA server starts successfully."""
    server = OPCUAServer()
    try:
        await server.setup()
        assert True  # Server started successfully
    except Exception as e:
        assert False, f"Server failed to start: {str(e)}"
    finally:
        await server.stop()

@pytest.mark.asyncio
async def test_connect_to_server():
    """Test connecting to the OPCUA server as a client."""
    client = Client(SERVER_URL)
    try:
        await client.connect()
        assert client.connected, "Failed to connect to OPCUA server"
        root = await client.get_root_node()
        assert root is not None, "Root node not found"
    except Exception as e:
        assert False, f"Connection error: {str(e)}"
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_read_variable():
    """Test reading a variable from the OPCUA server."""
    client = Client(SERVER_URL)
    try:
        await client.connect()
        # Assuming "variable1" is under MyObject in namespace
        namespace_uri = "http://example.com/opcua/server"
        idx = await client.get_namespace_index(namespace_uri)
        node = client.get_node(f"ns={idx};s=MyObject.variable1")
        value = await node.get_value()
        assert value is not None, "Failed to read variable value"
        print(f"Variable1 value: {value}")
    except Exception as e:
        assert False, f"Read error: {str(e)}"
    finally:
        await client.disconnect()