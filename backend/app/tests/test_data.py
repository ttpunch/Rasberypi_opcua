import asyncio
from fastapi.testclient import TestClient
import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import after adding to path
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_data():
    """Test retrieving data from the OPCUA server."""
    response = client.get("/data/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], dict)

@pytest.mark.asyncio
async def test_update_data():
    """Test updating data on the OPCUA server."""
    response = client.post("/data/", json={"variable": "variable1", "value": 42})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Updated variable1 successfully"