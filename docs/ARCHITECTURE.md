# 🏗️ OllamaStack Architecture Guide

This document provides a comprehensive overview of the OllamaStack architecture, design decisions, and system components.

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability Considerations](#scalability-considerations)
- [Security Architecture](#security-architecture)

## System Overview

OllamaStack follows a **microservices-inspired architecture** with clear separation of concerns between the frontend, backend, and LLM services. The system is designed for:

- **Modularity**: Each component can be developed, tested, and deployed independently
- **Scalability**: Components can be scaled horizontally based on demand
- **Maintainability**: Clean interfaces and well-defined boundaries
- **Extensibility**: Easy to add new features and integrations

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Next.js Frontend (Port 3000)                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  Components │ │   Pages     │ │    Hooks    │               │
│  │    React    │ │   Routing   │ │   Context   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   Routes    │ │  Services   │ │ Middleware  │               │
│  │   FastAPI   │ │  Business   │ │   CORS      │               │
│  │   OpenAPI   │ │   Logic     │ │   Auth      │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Orchestration                         │
├─────────────────────────────────────────────────────────────────┤
│  LangChain/LangGraph Services                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   Agents    │ │    Tools    │ │   Memory    │               │
│  │ LangGraph   │ │  Calculator │ │ Conversation│               │
│  │   Chains    │ │   Weather   │ │   Context   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Model Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Ollama Server (Port 11434)                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   Models    │ │ Model Mgmt  │ │   GPU/CPU   │               │
│  │  Llama3.2   │ │   Loading   │ │  Inference  │               │
│  │  CodeLlama  │ │   Caching   │ │  Batching   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Architecture (Next.js)

The frontend follows a **component-based architecture** with React best practices:

```
frontend/
├── components/           # Reusable UI components
│   ├── ChatInterface.tsx # Main chat component
│   ├── MessageList.tsx   # Message rendering
│   ├── Sidebar.tsx       # Navigation sidebar
│   └── Header.tsx        # Application header
├── pages/               # Next.js pages and routing
│   ├── _app.tsx         # Application wrapper
│   └── index.tsx        # Main page
├── lib/                 # Utilities and services
│   ├── api.ts           # API client
│   └── types.ts         # TypeScript definitions
├── hooks/               # Custom React hooks
│   ├── useChat.ts       # Chat state management
│   └── useApi.ts        # API interaction
└── styles/              # Styling and themes
    └── globals.css      # Global styles
```

#### Key Design Patterns

1. **Container/Presentational Components**
   - Containers handle state and business logic
   - Presentational components focus on UI rendering

2. **Custom Hooks for State Management**
   - `useChat` manages conversation state
   - `useApi` handles API interactions
   - `useSettings` manages user preferences

3. **Context API for Global State**
   - User preferences
   - Theme settings
   - Authentication state

### Backend Architecture (FastAPI)

The backend follows a **layered architecture** with clear separation:

```
backend/
├── app/
│   ├── main.py          # FastAPI application setup
│   ├── config.py        # Configuration management
│   ├── routes/          # API endpoints
│   │   ├── llm.py       # LLM chat endpoints
│   │   └── health.py    # Health check endpoints
│   ├── services/        # Business logic layer
│   │   ├── langchain_agent.py  # LLM orchestration
│   │   └── analytics.py        # Analytics service
│   ├── models/          # Data models and schemas
│   │   └── schemas.py   # Pydantic models
│   └── middleware/      # Custom middleware
│       ├── cors.py      # CORS handling
│       └── logging.py   # Request logging
└── tests/               # Test suite
    └── test_main.py     # API tests
```

#### Layered Architecture

1. **Presentation Layer** (`routes/`)
   - HTTP request handling
   - Input validation
   - Response formatting

2. **Business Logic Layer** (`services/`)
   - Core application logic
   - LLM interaction
   - Data processing

3. **Data Access Layer** (`models/`)
   - Data validation
   - Schema definitions
   - Database interactions (when implemented)

### LLM Orchestration (LangChain/LangGraph)

The LLM layer provides intelligent conversation handling:

```
LangChain Architecture:
┌─────────────────┐
│   Chat Agent    │
├─────────────────┤
│ ┌─────────────┐ │
│ │   Memory    │ │ ← Conversation history
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │    Tools    │ │ ← Calculator, Weather, etc.
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │    LLM      │ │ ← Ollama integration
│ └─────────────┘ │
└─────────────────┘
```

#### Agent Components

1. **Memory Management**
   - Conversation buffer window memory
   - Context-aware responses
   - History pruning for efficiency

2. **Tool Integration**
   - Calculator for math operations
   - Text analyzer for content analysis
   - Timestamp for temporal queries
   - Extensible tool framework

3. **Prompt Engineering**
   - Structured prompt templates
   - Context injection
   - Role-based prompting

## Data Flow

### Chat Request Flow

```
1. User Input (Frontend)
   │
   ▼
2. API Request (HTTP POST /api/v1/chat)
   │
   ▼
3. Request Validation (Pydantic)
   │
   ▼
4. Agent Processing (LangChain)
   │
   ├── Memory Retrieval
   ├── Tool Execution (if needed)
   └── LLM Inference (Ollama)
   │
   ▼
5. Response Generation
   │
   ▼
6. Response Validation & Formatting
   │
   ▼
7. HTTP Response (JSON)
   │
   ▼
8. UI Update (React State)
```

### Error Handling Flow

```
Error Occurs
│
├── Frontend Error
│   ├── Network Error → Retry Logic
│   ├── Validation Error → User Feedback
│   └── UI Error → Error Boundary
│
└── Backend Error
    ├── Validation Error → 400 Response
    ├── LLM Error → Fallback Response
    ├── Tool Error → Error Message
    └── System Error → 500 Response
```

## Technology Stack

### Frontend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 14 | React framework with SSR |
| Language | TypeScript | Type safety and developer experience |
| Styling | Tailwind CSS | Utility-first CSS framework |
| State Management | React Hooks + Context | Client-side state management |
| HTTP Client | Axios | API communication with interceptors |
| Build Tool | Next.js built-in | Webpack-based bundling |

### Backend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | Modern Python web framework |
| Language | Python 3.11+ | Backend development |
| Validation | Pydantic | Data validation and serialization |
| AI Framework | LangChain | LLM application framework |
| Agent Framework | LangGraph | Agent orchestration |
| ASGI Server | Uvicorn | Production ASGI server |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Application packaging |
| Orchestration | Docker Compose | Multi-service management |
| LLM Runtime | Ollama | Local LLM hosting |
| Reverse Proxy | Nginx | Load balancing and SSL |
| Monitoring | Built-in logging | Application monitoring |

## Design Patterns

### 1. Repository Pattern (Backend)

```python
class ConversationRepository:
    async def save_conversation(self, conversation: Conversation) -> str:
        # Database interaction logic
        pass
    
    async def get_conversation(self, conversation_id: str) -> Conversation:
        # Retrieval logic
        pass
```

### 2. Factory Pattern (LLM Models)

```python
class LLMFactory:
    @staticmethod
    def create_llm(model_type: str) -> BaseLLM:
        if model_type == "llama":
            return OllamaLLM(model="llama3.2")
        elif model_type == "codellama":
            return OllamaLLM(model="codellama")
        else:
            raise ValueError(f"Unknown model type: {model_type}")
```

### 3. Observer Pattern (Event System)

```python
class EventManager:
    def __init__(self):
        self.observers = defaultdict(list)
    
    def subscribe(self, event_type: str, callback: Callable):
        self.observers[event_type].append(callback)
    
    async def emit(self, event_type: str, data: dict):
        for callback in self.observers[event_type]:
            await callback(data)
```

### 4. Strategy Pattern (Tool Selection)

```python
class ToolStrategy:
    def select_tools(self, query: str) -> List[Tool]:
        # Implement tool selection logic
        pass

class MathToolStrategy(ToolStrategy):
    def select_tools(self, query: str) -> List[Tool]:
        if any(op in query for op in ['+', '-', '*', '/']):
            return [calculator_tool]
        return []
```

### 5. Middleware Pattern (Request Processing)

```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request processed in {process_time:.3f}s")
    return response
```

## Scalability Considerations

### Horizontal Scaling

1. **Frontend Scaling**
   - CDN for static assets
   - Multiple frontend instances behind load balancer
   - Client-side caching

2. **Backend Scaling**
   - Multiple FastAPI instances
   - Load balancing with session affinity
   - Stateless design for easy scaling

3. **LLM Scaling**
   - Multiple Ollama instances
   - Model sharding for large models
   - Request queuing and batching

### Vertical Scaling

1. **Resource Optimization**
   - Memory management for LLM models
   - CPU optimization for inference
   - GPU utilization when available

2. **Caching Strategy**
   - Response caching for common queries
   - Model loading optimization
   - Conversation context caching

### Database Scaling (Future)

```python
# Database scaling considerations
class DatabaseScaling:
    # Read replicas for query scaling
    read_db = create_engine(READ_DATABASE_URL)
    write_db = create_engine(WRITE_DATABASE_URL)
    
    # Connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600
    )
    
    # Query optimization
    def get_conversations_optimized(self, user_id: str, limit: int = 50):
        # Use indexes and pagination
        return session.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.created_at.desc())\
            .limit(limit)\
            .all()
```

## Security Architecture

### Authentication & Authorization

```python
# JWT-based authentication (future implementation)
class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_access_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")
```

### Input Validation & Sanitization

```python
# Pydantic models for validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9-_]+$')
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    
    @validator('message')
    def sanitize_message(cls, v):
        # Remove potentially harmful content
        return html.escape(v.strip())
```

### Security Headers

```python
# Security middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/v1/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request):
    # Chat logic with rate limiting
    pass
```

### Data Privacy

1. **Local Processing**
   - All LLM inference happens locally
   - No data sent to external APIs
   - User conversations stay on infrastructure

2. **Data Encryption**
   - HTTPS for all communications
   - Environment variable encryption
   - Database encryption at rest (when implemented)

3. **Audit Logging**
   - Request/response logging
   - User action tracking
   - Security event monitoring

---

This architecture guide provides the foundation for understanding, extending, and maintaining the OllamaStack system. The modular design ensures that each component can evolve independently while maintaining system coherence and performance. 