import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Settings
    app_name: str = "OllamaStack API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS Settings
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    
    # Ollama Settings
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: int = 300
    
    # LangChain Settings
    langchain_verbose: bool = False
    langchain_cache: bool = True
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 