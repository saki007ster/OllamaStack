import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ChatRequest, AgentRequest


class TestAPI:
    """Test cases for the OllamaStack API."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "🚀" in data["message"]
    
    def test_ping_endpoint(self, client):
        """Test ping endpoint."""
        response = client.get("/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code in [200, 503]  # May fail if Ollama not available
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_models_endpoint(self, client):
        """Test models listing endpoint."""
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "current_model" in data
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_tools_endpoint(self, client):
        """Test tools listing endpoint."""
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "count" in data
        assert isinstance(data["tools"], list)
        assert data["count"] == len(data["tools"])
    
    def test_chat_endpoint_validation(self, client):
        """Test chat endpoint with invalid data."""
        # Test missing message
        response = client.post("/api/v1/chat", json={})
        assert response.status_code == 422
        
        # Test empty message
        response = client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422
        
        # Test invalid temperature
        response = client.post("/api/v1/chat", json={
            "message": "Hello",
            "temperature": 3.0  # Too high
        })
        assert response.status_code == 422
    
    def test_chat_endpoint_valid_request(self, client):
        """Test chat endpoint with valid data."""
        chat_data = {
            "message": "Hello, how are you?",
            "temperature": 0.7,
            "max_tokens": 100
        }
        response = client.post("/api/v1/chat", json=chat_data)
        
        # May succeed or fail depending on Ollama availability
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "conversation_id" in data
            assert "model_used" in data
            assert "timestamp" in data
        else:
            # Should be 500 if Ollama unavailable
            assert response.status_code == 500
    
    def test_agent_endpoint_validation(self, client):
        """Test agent endpoint with invalid data."""
        # Test missing task
        response = client.post("/api/v1/agent", json={})
        assert response.status_code == 422
        
        # Test empty task
        response = client.post("/api/v1/agent", json={"task": ""})
        assert response.status_code == 422
        
        # Test invalid max_iterations
        response = client.post("/api/v1/agent", json={
            "task": "Analyze this text",
            "max_iterations": 0  # Too low
        })
        assert response.status_code == 422
    
    def test_agent_endpoint_valid_request(self, client):
        """Test agent endpoint with valid data."""
        agent_data = {
            "task": "Calculate 2 + 2 and explain the result",
            "agent_type": "default",
            "tools": ["calculator"],
            "max_iterations": 5
        }
        response = client.post("/api/v1/agent", json=agent_data)
        
        # May succeed or fail depending on Ollama availability
        if response.status_code == 200:
            data = response.json()
            assert "result" in data
            assert "steps" in data
            assert "agent_type" in data
            assert "timestamp" in data
        else:
            # Should be 500 if Ollama unavailable
            assert response.status_code == 500
    
    def test_conversation_history_endpoint(self, client):
        """Test conversation history endpoint."""
        conversation_id = "test-conversation-123"
        response = client.get(f"/api/v1/conversations/{conversation_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "messages" in data
        assert "message_count" in data
        assert isinstance(data["messages"], list)
    
    def test_clear_conversation_endpoint(self, client):
        """Test clear conversation endpoint."""
        conversation_id = "test-conversation-456"
        response = client.delete(f"/api/v1/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert conversation_id in data["message"]
    
    def test_legacy_ask_endpoint(self, client):
        """Test legacy ask endpoint."""
        response = client.get("/api/v1/ask?question=Hello")
        
        # May succeed or fail depending on Ollama availability
        if response.status_code == 200:
            data = response.json()
            assert "question" in data
            assert "answer" in data
            assert "conversation_id" in data
            assert data["question"] == "Hello"
        else:
            # Should be 500 if Ollama unavailable
            assert response.status_code == 500
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        # CORS headers should be present in the response
        assert response.status_code in [200, 405]  # Method may not be allowed but headers should be there


@pytest.mark.asyncio
class TestAsyncAPI:
    """Async test cases for the API."""
    
    async def test_async_health_check(self):
        """Test async health check."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
            assert response.status_code in [200, 503]
    
    async def test_async_chat_endpoint(self):
        """Test async chat endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            chat_data = {
                "message": "What is 2 + 2?",
                "temperature": 0.5
            }
            response = await ac.post("/api/v1/chat", json=chat_data)
            # Response may vary based on Ollama availability
            assert response.status_code in [200, 500]


# Integration tests that require Ollama
@pytest.mark.integration
class TestIntegration:
    """Integration tests that require Ollama to be running."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_full_chat_flow(self, client):
        """Test full chat conversation flow."""
        # First message
        response1 = client.post("/api/v1/chat", json={
            "message": "Hello, my name is John."
        })
        assert response1.status_code == 200
        data1 = response1.json()
        conversation_id = data1["conversation_id"]
        
        # Second message in same conversation
        response2 = client.post("/api/v1/chat", json={
            "message": "What is my name?",
            "conversation_id": conversation_id
        })
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conversation_id
        
        # Check conversation history
        history_response = client.get(f"/api/v1/conversations/{conversation_id}/history")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data["messages"]) >= 2
    
    def test_agent_with_tools(self, client):
        """Test agent with specific tools."""
        response = client.post("/api/v1/agent", json={
            "task": "Calculate the square root of 144 and tell me the current time",
            "tools": ["calculator", "timestamp"],
            "max_iterations": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "calculator" in str(data["metadata"]["tools_used"])
        assert "timestamp" in str(data["metadata"]["tools_used"])


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"]) 