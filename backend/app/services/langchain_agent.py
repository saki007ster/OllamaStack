import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from loguru import logger

from app.config import settings


class ConversationState(BaseModel):
    """State for conversation management."""
    messages: List[BaseMessage] = []
    conversation_id: str = ""
    metadata: Dict[str, Any] = {}


class OllamaAgentService:
    """Enhanced LangChain agent service with LangGraph integration."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.memory_store: Dict[str, ConversationBufferWindowMemory] = {}
        self.tools = self._initialize_tools()
        logger.info("OllamaAgentService initialized successfully")
    
    def _initialize_llm(self) -> OllamaLLM:
        """Initialize the Ollama LLM."""
        try:
            llm = OllamaLLM(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=0.7,
                verbose=settings.langchain_verbose,
                timeout=settings.ollama_timeout
            )
            logger.info(f"LLM initialized with model: {settings.ollama_model}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize available tools for the agent."""
        tools = [
            Tool(
                name="calculator",
                description="Useful for mathematical calculations. Input should be a mathematical expression.",
                func=self._calculator_tool
            ),
            Tool(
                name="text_analyzer",
                description="Analyze text for sentiment, word count, and key phrases.",
                func=self._text_analyzer_tool
            ),
            Tool(
                name="timestamp",
                description="Get current timestamp and date information.",
                func=self._timestamp_tool
            )
        ]
        logger.info(f"Initialized {len(tools)} tools for agent")
        return tools
    
    def _calculator_tool(self, expression: str) -> str:
        """Simple calculator tool."""
        try:
            # Safe evaluation of mathematical expressions
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _text_analyzer_tool(self, text: str) -> str:
        """Text analysis tool."""
        try:
            word_count = len(text.split())
            char_count = len(text)
            sentences = text.count('.') + text.count('!') + text.count('?')
            
            # Simple sentiment analysis based on keywords
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate']
            
            positive_count = sum(1 for word in positive_words if word in text.lower())
            negative_count = sum(1 for word in negative_words if word in text.lower())
            
            if positive_count > negative_count:
                sentiment = "Positive"
            elif negative_count > positive_count:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return f"Text Analysis:\n- Word count: {word_count}\n- Character count: {char_count}\n- Sentences: {sentences}\n- Sentiment: {sentiment}"
        except Exception as e:
            return f"Error analyzing text: {str(e)}"
    
    def _timestamp_tool(self, query: str = "") -> str:
        """Get current timestamp information."""
        now = datetime.now()
        return f"Current timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    
    def get_memory(self, conversation_id: str) -> ConversationBufferWindowMemory:
        """Get or create memory for a conversation."""
        if conversation_id not in self.memory_store:
            self.memory_store[conversation_id] = ConversationBufferWindowMemory(
                k=10,  # Keep last 10 exchanges
                return_messages=True,
                memory_key="chat_history"
            )
        return self.memory_store[conversation_id]
    
    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Process a chat message."""
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Get conversation memory
            memory = self.get_memory(conversation_id)
            
            # Update LLM temperature if specified
            if hasattr(self.llm, 'temperature'):
                self.llm.temperature = temperature
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant powered by Ollama. You have access to various tools to help answer questions and perform tasks."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Add user message to memory
            memory.chat_memory.add_user_message(message)
            
            # Generate response
            response = await self._generate_response(prompt, message, memory)
            
            # Add AI response to memory
            memory.chat_memory.add_ai_message(response)
            
            return {
                "message": response,
                "conversation_id": conversation_id,
                "model_used": model or settings.ollama_model,
                "timestamp": datetime.now(),
                "metadata": {
                    "temperature": temperature,
                    "memory_length": len(memory.chat_memory.messages)
                }
            }
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    async def _generate_response(self, prompt, message: str, memory) -> str:
        """Generate response using the LLM."""
        try:
            # Try LangChain first
            try:
                # Format the prompt with chat history
                formatted_prompt = prompt.format(
                    input=message,
                    chat_history=memory.chat_memory.messages
                )
                
                # Generate response
                response = self.llm.invoke(formatted_prompt)
                return response
            except Exception as langchain_error:
                logger.warning(f"LangChain failed, using direct HTTP: {langchain_error}")
                
                # Fallback to direct HTTP call to Ollama
                import requests
                
                # Format chat history for prompt
                chat_context = ""
                if hasattr(memory, 'chat_memory') and memory.chat_memory.messages:
                    recent_messages = memory.chat_memory.messages[-6:]  # Last 3 exchanges
                    for msg in recent_messages:
                        role = "Human" if msg.type == "human" else "Assistant"
                        chat_context += f"{role}: {msg.content}\n"
                
                # Create full prompt
                full_prompt = f"""You are a helpful AI assistant powered by Ollama. You have access to various tools to help answer questions and perform tasks.

{chat_context}
Human: {message}
Assistant:"""
                
                # Make direct HTTP request to Ollama
                payload = {
                    'model': settings.ollama_model,
                    'prompt': full_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 1000
                    }
                }
                
                response = requests.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', 'No response generated')
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def run_agent(
        self,
        task: str,
        agent_type: str = "default",
        tools: Optional[List[str]] = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Run an agent to complete a task."""
        try:
            conversation_id = str(uuid.uuid4())
            execution_steps = []
            
            # Filter tools based on request
            available_tools = self.tools
            if tools:
                available_tools = [t for t in self.tools if t.name in tools]
            
            # Create agent prompt
            agent_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a {agent_type} agent. Use the available tools to complete the given task.
                Available tools: {', '.join([t.name for t in available_tools])}
                
                Think step by step and use tools when necessary to provide accurate and helpful responses."""),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # For now, use simple LLM response with tool calling
            # In a full implementation, you'd use LangGraph for more complex agent workflows
            
            step = {
                "step": 1,
                "action": "analyzing_task",
                "input": task,
                "timestamp": datetime.now().isoformat()
            }
            execution_steps.append(step)
            
            # Generate response
            response = self.llm.invoke(f"Task: {task}\n\nPlease complete this task step by step.")
            
            step = {
                "step": 2,
                "action": "generating_response",
                "output": response,
                "timestamp": datetime.now().isoformat()
            }
            execution_steps.append(step)
            
            return {
                "result": response,
                "steps": execution_steps,
                "agent_type": agent_type,
                "timestamp": datetime.now(),
                "metadata": {
                    "tools_used": [t.name for t in available_tools],
                    "max_iterations": max_iterations,
                    "conversation_id": conversation_id
                }
            }
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Ollama service."""
        try:
            # Try LangChain first, then fall back to HTTP
            try:
                test_response = self.llm.invoke("Say 'OK' if you're working correctly.")
                status = "healthy" if test_response else "unhealthy"
                
                return {
                    "status": status,
                    "model": settings.ollama_model,
                    "base_url": settings.ollama_base_url,
                    "response": test_response[:50] if test_response else None
                }
            except Exception:
                # Fall back to direct HTTP health check
                import requests
                
                # Test basic connectivity
                response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_available = any(m['name'].startswith(settings.ollama_model) for m in models)
                    
                    return {
                        "status": "healthy" if model_available else "degraded",
                        "model": settings.ollama_model,
                        "base_url": settings.ollama_base_url,
                        "available_models": [m['name'] for m in models],
                        "fallback_mode": True
                    }
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": settings.ollama_model,
                "base_url": settings.ollama_base_url
            }


# Global service instance
agent_service = OllamaAgentService()


# Legacy function for backward compatibility
def run_agent(question: str) -> str:
    """Legacy function for backward compatibility."""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent_service.chat(question))
        return result["message"]
    except Exception as e:
        logger.error(f"Error in legacy run_agent: {e}")
        return f"Error: {str(e)}"
