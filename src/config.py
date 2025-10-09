"""
Configuration management for KubeGenie
Handles environment variables and application settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # LangSmith Configuration
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = True
    
    # Kubernetes Configuration
    kubeconfig: Optional[str] = None
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    
    # Gradio Interface Configuration
    gradio_host: str = "127.0.0.1"
    gradio_port: int = 7860
    gradio_share: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings