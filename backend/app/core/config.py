"""
Configuration management for KubeGenie Backend
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_DEBUG: bool = Field(default=False, env="API_DEBUG")
    API_SECRET_KEY: str = Field(default="dev-secret-key", env="API_SECRET_KEY")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./kubegenie.db", env="DATABASE_URL")
    
    # Kubernetes Configuration
    KUBECONFIG: Optional[str] = Field(default=None, env="KUBECONFIG")
    DEFAULT_NAMESPACE: str = Field(default="default", env="DEFAULT_NAMESPACE")
    
    # Crossplane Configuration
    CROSSPLANE_NAMESPACE: str = Field(default="crossplane-system", env="CROSSPLANE_NAMESPACE")
    
    # Authentication & Authorization
    AUTH_ENABLED: bool = Field(default=True, env="AUTH_ENABLED")
    JWT_SECRET: str = Field(default="jwt-secret-key", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Safety & Security
    ENABLE_AUDIT_LOG: bool = Field(default=True, env="ENABLE_AUDIT_LOG")
    REQUIRE_APPROVAL: bool = Field(default=True, env="REQUIRE_APPROVAL")
    ENABLE_COST_ESTIMATION: bool = Field(default=True, env="ENABLE_COST_ESTIMATION")
    MAX_RESOURCE_LIMIT: int = Field(default=100, env="MAX_RESOURCE_LIMIT")
    
    # Observability
    PROMETHEUS_URL: Optional[str] = Field(default=None, env="PROMETHEUS_URL")
    GRAFANA_URL: Optional[str] = Field(default=None, env="GRAFANA_URL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # External Integrations
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    TEAMS_WEBHOOK_URL: Optional[str] = Field(default=None, env="TEAMS_WEBHOOK_URL")
    
    # Storage Configuration
    BACKUP_STORAGE_PATH: str = Field(default="/var/lib/kubegenie/backups", env="BACKUP_STORAGE_PATH")
    ENABLE_BACKUP_ENCRYPTION: bool = Field(default=True, env="ENABLE_BACKUP_ENCRYPTION")
    
    # Development
    ENABLE_CORS: bool = Field(default=True, env="ENABLE_CORS")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    ENABLE_LLM: bool = Field(default=True, env="ENABLE_LLM")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings