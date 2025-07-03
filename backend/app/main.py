import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import llm
from app.config import settings
from app.models.schemas import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 OllamaStack API starting up...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"Ollama URL: {settings.ollama_base_url}")
    logger.info(f"Model: {settings.ollama_model}")
    
    try:
        # Test Ollama connection
        from app.services.langchain_agent import agent_service
        health = await agent_service.health_check()
        if health["status"] == "healthy":
            logger.success("✅ Ollama connection successful")
        else:
            logger.warning(f"⚠️ Ollama connection issues: {health.get('error', 'Unknown')}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Ollama: {e}")
    
    yield
    
    # Shutdown
    logger.info("🔄 OllamaStack API shutting down...")
    logger.success("✅ Shutdown complete")


# Configure logging
def configure_logging():
    """Configure application logging."""
    logger.remove()  # Remove default handler
    
    # Add console logging
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file logging
    logger.add(
        "logs/app.log",
        format=settings.log_format,
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )


# Initialize logging
configure_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A modern, production-ready boilerplate for AI applications using FastAPI, LangChain, LangGraph, and Ollama.",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Logging middleware to track requests and responses.
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-API-Version"] = settings.app_version
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s")
        raise


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP {exc.status_code}",
            detail=exc.detail
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation Error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail=f"Invalid request data: {exc.errors()}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again later." if not settings.debug else str(exc)
        ).dict()
    )


# Include routers
app.include_router(llm.router)


@app.get("/")
async def read_root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "🚀 OllamaStack API is running!",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
        "timestamp": time.time(),
        "environment": "development" if settings.debug else "production"
    }


@app.get("/ping")
async def ping():
    """
    Simple ping endpoint for load balancer health checks.
    """
    return {"status": "ok", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
