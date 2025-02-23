import asyncio
from fastapi.testclient import TestClient
from main import app
import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_add_config():
    """Test adding a namespace and variables."""
    response = client.post("/config/", json={
        "namespace": "http://example.com/opcua/server",
        "variables": [
            {"name": "test_variable", "value": 42}
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Configuration updated successfully"

@pytest.mark.asyncio
async def test_get_config():
    """Test retrieving the current configuration."""
    response = client.get("/config/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["config"], dict)