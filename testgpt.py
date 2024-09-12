import os
import pytest
from fastapi.testclient import TestClient
from main import app  # Import the FastAPI app from your main file

client = TestClient(app)

@pytest.fixture
def set_openai_api_key(monkeypatch):
    # Set the OPENAI_API_KEY environment variable for the test
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        monkeypatch.setenv("OPENAI_API_KEY", api_key)
    else:
        pytest.skip("OPENAI_API_KEY not set in environment variables")

def test_robloxgpt_endpoint(set_openai_api_key):
    response = client.post("/robloxgpt", json={
        "message": "Hello, robloxgpt!",
        "player_id": "test_player",
        "npc_id": "test_npc",
        "limit": 200
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_robloxgpt_endpoint_no_api_key(monkeypatch):
    # Unset the OPENAI_API_KEY environment variable for the test
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/robloxgpt", json={
        "message": "Hello, robloxgpt!",
        "player_id": "test_player",
        "npc_id": "test_npc",
        "limit": 200
    })
    assert response.status_code == 500
    assert response.json()["message"] == "OpenAI API key not found"

def test_robloxgpt_endpoint_invalid_input():
    response = client.post("/robloxgpt", json={"message": "Invalid input"})
    assert response.status_code == 422
    assert "detail" in response.json()