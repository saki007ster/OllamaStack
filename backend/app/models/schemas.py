from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum tokens in response")


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    message: str = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation ID")
    model_used: str = Field(..., description="Model used for generation")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AgentRequest(BaseModel):
    """Request model for agent endpoints."""
    task: str = Field(..., min_length=1, max_length=10000, description="Task for the agent to perform")
    agent_type: Optional[str] = Field("default", description="Type of agent to use")
    tools: Optional[List[str]] = Field(default=[], description="List of tools the agent can use")
    max_iterations: Optional[int] = Field(10, ge=1, le=50, description="Maximum iterations for agent")


class AgentResponse(BaseModel):
    """Response model for agent endpoints."""
    result: str = Field(..., description="Agent execution result")
    steps: List[Dict[str, Any]] = Field(default=[], description="Agent execution steps")
    agent_type: str = Field(..., description="Type of agent used")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API version")
    ollama_status: str = Field(..., description="Ollama service status")
    uptime: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = Field(None, description="Request ID for tracking") 