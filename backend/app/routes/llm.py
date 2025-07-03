import uuid
import time
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import (
    ChatRequest, ChatResponse, AgentRequest, AgentResponse,
    HealthResponse, ErrorResponse
)
from app.services.langchain_agent import agent_service
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["LLM"])

# Track service start time for uptime calculation
_start_time = time.time()


def get_uptime() -> float:
    """Calculate service uptime in seconds."""
    return time.time() - _start_time


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthResponse: Current service status and Ollama connectivity
    """
    try:
        ollama_health = await agent_service.health_check()
        
        return HealthResponse(
            status="healthy" if ollama_health["status"] == "healthy" else "degraded",
            version=settings.app_version,
            ollama_status=ollama_health["status"],
            uptime=get_uptime()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI assistant.
    
    Args:
        request: Chat request containing message and optional parameters
        
    Returns:
        ChatResponse: AI response with conversation metadata
    """
    try:
        logger.info(f"Chat request received: {request.message[:50]}...")
        
        result = await agent_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/agent", response_model=AgentResponse)
async def run_agent_task(request: AgentRequest):
    """
    Execute a task using an AI agent.
    
    Args:
        request: Agent request containing task and configuration
        
    Returns:
        AgentResponse: Agent execution result with steps and metadata
    """
    try:
        logger.info(f"Agent task received: {request.task[:50]}...")
        
        result = await agent_service.run_agent(
            task=request.task,
            agent_type=request.agent_type,
            tools=request.tools,
            max_iterations=request.max_iterations
        )
        
        return AgentResponse(**result)
        
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """
    Retrieve conversation history for a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        
    Returns:
        Conversation history and metadata
    """
    try:
        memory = agent_service.get_memory(conversation_id)
        messages = []
        
        for message in memory.chat_memory.messages:
            messages.append({
                "role": "user" if hasattr(message, 'content') and isinstance(message, type(memory.chat_memory.messages[0])) else "assistant",
                "content": message.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear conversation history for a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        
    Returns:
        Confirmation of conversation clearance
    """
    try:
        if conversation_id in agent_service.memory_store:
            del agent_service.memory_store[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")
        
        return {
            "message": f"Conversation {conversation_id} cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation: {str(e)}"
        )


@router.get("/models")
async def list_available_models():
    """
    List available models and their information.
    
    Returns:
        List of available models and current configuration
    """
    try:
        return {
            "current_model": settings.ollama_model,
            "ollama_base_url": settings.ollama_base_url,
            "models": [
                {
                    "name": settings.ollama_model,
                    "type": "ollama",
                    "status": "active"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/tools")
async def list_available_tools():
    """
    List available tools for agents.
    
    Returns:
        List of available tools with descriptions
    """
    try:
        tools_info = []
        for tool in agent_service.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "type": "function"
            })
        
        return {
            "tools": tools_info,
            "count": len(tools_info),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


# Legacy endpoint for backward compatibility
@router.get("/ask")
async def ask(question: str):
    """
    Legacy endpoint for simple Q&A (deprecated - use /chat instead).
    
    Args:
        question: Question to ask the AI
        
    Returns:
        Simple Q&A response
    """
    try:
        logger.warning("Legacy /ask endpoint used - consider migrating to /chat")
        
        result = await agent_service.chat(message=question)
        
        return {
            "question": question,
            "answer": result["message"],
            "conversation_id": result["conversation_id"],
            "timestamp": result["timestamp"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Legacy ask error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question processing failed: {str(e)}"
        )
