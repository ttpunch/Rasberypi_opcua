import asyncio
import websockets
import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.main import app

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test establishing a WebSocket connection and receiving updates."""
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send a test message (optional, depending on backend implementation)
        await websocket.send(json.dumps({"action": "subscribe"}))
        
        # Wait for an update (simulating real-time data)
        response = await websocket.recv()
        data = json.loads(response)
        assert data["event"] == "update"
        assert isinstance(data["data"], dict)