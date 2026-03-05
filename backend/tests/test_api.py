import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    return agent


@pytest.fixture
def client(mock_agent):
    with patch("main.get_agent", return_value=mock_agent):
        from main import app
        yield TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestChatEndpoint:
    @patch("main.run_agent", new_callable=AsyncMock)
    def test_success(self, mock_run_agent, client):
        mock_run_agent.return_value = {
            "response": "It's sunny in Tokyo!",
            "tool_calls": [{"tool": "get_current_weather", "args": {"city": "Tokyo"}}],
            "cached": False,
            "fallback": False,
        }
        resp = client.post("/api/chat", json={"message": "Weather in Tokyo?"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == "It's sunny in Tokyo!"
        assert data["cached"] is False
        assert data["fallback"] is False

    @patch("main.run_agent", new_callable=AsyncMock)
    def test_cached_response(self, mock_run_agent, client):
        mock_run_agent.return_value = {
            "response": "Sunny!", "tool_calls": [],
            "cached": True, "fallback": False,
        }
        resp = client.post("/api/chat", json={"message": "Weather?"})
        assert resp.json()["cached"] is True
        assert resp.json()["fallback"] is False

    @patch("main.run_agent", new_callable=AsyncMock)
    def test_fallback_response(self, mock_run_agent, client):
        mock_run_agent.return_value = {
            "response": "Sunny!", "tool_calls": [],
            "cached": False, "fallback": True,
        }
        resp = client.post("/api/chat", json={"message": "Weather?"})
        assert resp.json()["fallback"] is True

    def test_empty_message(self, client):
        resp = client.post("/api/chat", json={"message": "   "})
        assert resp.status_code == 400

    def test_missing_message(self, client):
        resp = client.post("/api/chat", json={})
        assert resp.status_code == 422

    @patch("main.run_agent", new_callable=AsyncMock)
    def test_agent_error(self, mock_run_agent, client):
        mock_run_agent.side_effect = RuntimeError("LLM failed")
        resp = client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code == 500

    @patch("main.run_agent", new_callable=AsyncMock)
    def test_with_chat_history(self, mock_run_agent, client):
        mock_run_agent.return_value = {
            "response": "Still sunny!", "tool_calls": [],
            "cached": False, "fallback": False,
        }
        resp = client.post("/api/chat", json={
            "message": "And now?",
            "chat_history": [
                {"role": "user", "content": "Weather?"},
                {"role": "assistant", "content": "Sunny!"},
            ],
        })
        assert resp.status_code == 200
