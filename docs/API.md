# 📚 OllamaStack API Documentation

This document provides comprehensive documentation for the OllamaStack REST API.

## Table of Contents

- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [WebSocket Events](#websocket-events)
- [SDKs & Examples](#sdks--examples)

## API Overview

The OllamaStack API is a RESTful API built with FastAPI that provides endpoints for:

- **Chat Operations**: Send messages to LLM and receive responses
- **Conversation Management**: Create, list, and manage conversations  
- **Health Monitoring**: Check service status and health
- **Agent Tools**: Access calculator, text analysis, and other tools
- **Model Management**: List and configure available models

### OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Authentication

Currently, the API does not require authentication for development usage. For production deployments, implement one of these authentication methods:

### JWT Authentication (Recommended)

```python
# Example JWT middleware implementation
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### API Key Authentication

```python
# Example API key middleware
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API key")
    return x_api_key
```

## Base URL

| Environment | Base URL |
|-------------|----------|
| Development | `http://localhost:8000` |
| Production | `https://api.yourdomain.com` |

## Response Format

All API responses follow a consistent JSON format:

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "message",
      "issue": "Field is required"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Types

```python
from enum import Enum

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    LLM_ERROR = "LLM_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

## Rate Limiting

Rate limits are applied per IP address:

| Endpoint | Rate Limit | Burst |
|----------|------------|-------|
| `/api/v1/chat` | 10 requests/minute | 20 requests |
| `/api/v1/health` | 60 requests/minute | 100 requests |
| All other endpoints | 30 requests/minute | 60 requests |

### Rate Limit Headers

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1640995200
```

## Endpoints

### Health Check

#### GET `/api/v1/health`

Check the health status of the API and its dependencies.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "ollama": "healthy",
    "langchain": "healthy"
  },
  "uptime": 86400
}
```

**Status Values:**
- `healthy`: All services operational
- `degraded`: Some services experiencing issues
- `unhealthy`: Critical services down

### Chat Operations

#### POST `/api/v1/chat`

Send a message to the LLM and receive a response.

**Request Body:**

```json
{
  "message": "What is machine learning?",
  "conversation_id": "conv_123",
  "model": "llama3.2",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false,
  "tools": ["calculator", "timestamp"]
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | ✅ | - | User message (1-4000 chars) |
| `conversation_id` | string | ❌ | auto-generated | Conversation identifier |
| `model` | string | ❌ | `llama3.2` | Model to use for response |
| `temperature` | float | ❌ | `0.7` | Response creativity (0.0-2.0) |
| `max_tokens` | integer | ❌ | `1000` | Maximum response length |
| `stream` | boolean | ❌ | `false` | Enable streaming response |
| `tools` | array | ❌ | `[]` | Tools available to agent |

**Response:**

```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "conversation_id": "conv_123",
  "model": "llama3.2",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 150,
    "total_tokens": 165
  },
  "tools_used": ["calculator"],
  "response_time_ms": 2500,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Streaming Response:**

When `stream: true`, the response is sent as Server-Sent Events:

```
data: {"type": "start", "conversation_id": "conv_123"}

data: {"type": "token", "content": "Machine"}

data: {"type": "token", "content": " learning"}

data: {"type": "tool_call", "tool": "calculator", "input": "2+2"}

data: {"type": "tool_result", "tool": "calculator", "output": "4"}

data: {"type": "end", "usage": {"total_tokens": 165}}
```

#### GET `/api/v1/chat/{conversation_id}/history`

Retrieve conversation history.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conversation_id` | string | ✅ | Conversation identifier |
| `limit` | integer | ❌ | Number of messages (max 100) |
| `offset` | integer | ❌ | Pagination offset |

**Response:**

```json
{
  "conversation_id": "conv_123",
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "Hello!",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "id": "msg_2", 
      "role": "assistant",
      "content": "Hello! How can I help you today?",
      "timestamp": "2024-01-01T12:00:05Z",
      "usage": {
        "total_tokens": 25
      }
    }
  ],
  "total_messages": 2,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

### Conversation Management

#### GET `/api/v1/conversations`

List user conversations.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | ❌ | `20` | Results per page (1-100) |
| `offset` | integer | ❌ | `0` | Pagination offset |
| `sort` | string | ❌ | `updated_at` | Sort field |
| `order` | string | ❌ | `desc` | Sort order (asc/desc) |

**Response:**

```json
{
  "conversations": [
    {
      "id": "conv_123",
      "title": "Machine Learning Discussion", 
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:30:00Z",
      "message_count": 10,
      "model": "llama3.2"
    }
  ],
  "total_count": 5,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

#### POST `/api/v1/conversations`

Create a new conversation.

**Request Body:**

```json
{
  "title": "My New Conversation",
  "model": "llama3.2",
  "system_prompt": "You are a helpful assistant."
}
```

**Response:**

```json
{
  "id": "conv_456",
  "title": "My New Conversation",
  "created_at": "2024-01-01T12:00:00Z",
  "model": "llama3.2",
  "system_prompt": "You are a helpful assistant."
}
```

#### DELETE `/api/v1/conversations/{conversation_id}`

Delete a conversation.

**Response:**

```json
{
  "message": "Conversation deleted successfully",
  "conversation_id": "conv_123"
}
```

### Model Management

#### GET `/api/v1/models`

List available models.

**Response:**

```json
{
  "models": [
    {
      "name": "llama3.2",
      "size": "3.2B",
      "description": "Llama 3.2 base model",
      "status": "available",
      "capabilities": ["chat", "completion"],
      "context_length": 8192
    },
    {
      "name": "codellama",
      "size": "7B", 
      "description": "Code Llama for programming tasks",
      "status": "available",
      "capabilities": ["code", "chat"],
      "context_length": 16384
    }
  ]
}
```

#### GET `/api/v1/models/{model_name}/info`

Get detailed model information.

**Response:**

```json
{
  "name": "llama3.2",
  "version": "latest",
  "size": "3.2B",
  "parameters": 3200000000,
  "architecture": "transformer",
  "context_length": 8192,
  "vocabulary_size": 128256,
  "status": "loaded",
  "loaded_at": "2024-01-01T10:00:00Z",
  "memory_usage": "6.4GB"
}
```

### Tool Operations

#### GET `/api/v1/tools`

List available tools.

**Response:**

```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "Perform mathematical calculations",
      "parameters": {
        "expression": {
          "type": "string",
          "description": "Mathematical expression to evaluate"
        }
      },
      "examples": ["2 + 2", "sqrt(16)", "sin(pi/2)"]
    },
    {
      "name": "timestamp",
      "description": "Get current timestamp",
      "parameters": {},
      "examples": []
    }
  ]
}
```

#### POST `/api/v1/tools/{tool_name}/execute`

Execute a tool directly.

**Request Body:**

```json
{
  "parameters": {
    "expression": "2 + 2 * 3"
  }
}
```

**Response:**

```json
{
  "tool": "calculator",
  "input": {
    "expression": "2 + 2 * 3"
  },
  "output": "8",
  "execution_time_ms": 15,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Analytics

#### GET `/api/v1/analytics/usage`

Get usage analytics.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | ❌ | Start date (ISO 8601) |
| `end_date` | string | ❌ | End date (ISO 8601) |
| `granularity` | string | ❌ | Time granularity (hour/day/week) |

**Response:**

```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "metrics": {
    "total_messages": 1250,
    "total_conversations": 85,
    "total_tokens": 125000,
    "average_response_time_ms": 2300,
    "error_rate": 0.02
  },
  "breakdown": {
    "by_model": {
      "llama3.2": {"messages": 900, "tokens": 90000},
      "codellama": {"messages": 350, "tokens": 35000}
    },
    "by_tool": {
      "calculator": 45,
      "timestamp": 12
    }
  },
  "timeline": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "messages": 50,
      "tokens": 5000
    }
  ]
}
```

## WebSocket Events

### Connection

Connect to WebSocket for real-time events:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Event Types

#### Message Events

```json
{
  "type": "message",
  "data": {
    "conversation_id": "conv_123",
    "message": {
      "id": "msg_456",
      "role": "assistant", 
      "content": "Hello!",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

#### Typing Indicator

```json
{
  "type": "typing",
  "data": {
    "conversation_id": "conv_123",
    "is_typing": true
  }
}
```

#### Error Events

```json
{
  "type": "error",
  "data": {
    "code": "CONNECTION_ERROR",
    "message": "Failed to process request"
  }
}
```

## SDKs & Examples

### Python SDK

```python
import requests
from typing import Optional, Dict, Any

class OllamaStackClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, 
             message: str, 
             conversation_id: Optional[str] = None,
             model: str = "llama3.2",
             temperature: float = 0.7,
             stream: bool = False) -> Dict[str, Any]:
        """Send a chat message."""
        
        payload = {
            "message": message,
            "model": model,
            "temperature": temperature,
            "stream": stream
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = self.session.post(
            f"{self.base_url}/api/v1/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_conversations(self, limit: int = 20) -> Dict[str, Any]:
        """Get list of conversations."""
        
        response = self.session.get(
            f"{self.base_url}/api/v1/conversations",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()

# Usage example
client = OllamaStackClient()

# Send a message
response = client.chat("What is machine learning?")
print(response["response"])

# Check health
health = client.health_check()
print(f"Status: {health['status']}")
```

### JavaScript SDK

```javascript
class OllamaStackClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async chat({
        message,
        conversationId = null,
        model = 'llama3.2',
        temperature = 0.7,
        stream = false
    }) {
        const payload = {
            message,
            model,
            temperature,
            stream
        };
        
        if (conversationId) {
            payload.conversation_id = conversationId;
        }
        
        const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getConversations(limit = 20) {
        const response = await fetch(
            `${this.baseUrl}/api/v1/conversations?limit=${limit}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/api/v1/health`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage example
const client = new OllamaStackClient();

async function example() {
    try {
        // Send a message
        const response = await client.chat({
            message: "What is machine learning?"
        });
        console.log(response.response);
        
        // Check health
        const health = await client.healthCheck();
        console.log(`Status: ${health.status}`);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

example();
```

### cURL Examples

#### Send Chat Message

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "model": "llama3.2",
    "temperature": 0.7
  }'
```

#### List Conversations

```bash
curl -X GET "http://localhost:8000/api/v1/conversations?limit=10" \
  -H "Accept: application/json"
```

#### Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Accept: application/json"
```

#### Execute Tool

```bash
curl -X POST "http://localhost:8000/api/v1/tools/calculator/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "expression": "2 + 2 * 3"
    }
  }'
```

### Error Handling Examples

#### Python Error Handling

```python
from requests.exceptions import HTTPError, RequestException

try:
    response = client.chat("Hello")
except HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded")
    elif e.response.status_code == 500:
        print("Server error")
    else:
        print(f"HTTP error: {e.response.status_code}")
except RequestException as e:
    print(f"Request failed: {e}")
```

#### JavaScript Error Handling

```javascript
try {
    const response = await client.chat({ message: "Hello" });
} catch (error) {
    if (error.message.includes('429')) {
        console.log('Rate limit exceeded');
    } else if (error.message.includes('500')) {
        console.log('Server error');
    } else {
        console.log('Request failed:', error.message);
    }
}
```

---

This API documentation provides comprehensive coverage of all OllamaStack endpoints, including request/response formats, error handling, and practical examples in multiple programming languages. 