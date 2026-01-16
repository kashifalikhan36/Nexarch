"""
Production-Ready Configuration with Azure OpenAI
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Nexarch"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./nexarch.db"  # Change to PostgreSQL for production
    
    # Redis for caching (optional - falls back to in-memory)
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_TEMPERATURE: float = 0.7
    AZURE_OPENAI_MAX_TOKENS: int = 2000
    
    # Authentication & Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    API_KEY_PREFIX: str = "nex_"
    
    # Rate Limiting (per tenant)
    RATE_LIMIT_PER_MINUTE: int = 1000
    
    # Metrics thresholds
    HIGH_LATENCY_THRESHOLD_MS: int = 1000
    HIGH_ERROR_RATE_THRESHOLD: float = 0.05
    MAX_SYNC_CHAIN_DEPTH: int = 5
    MAX_FAN_OUT: int = 10
    
    # AI Generation Settings
    ENABLE_AI_GENERATION: bool = True
    MAX_WORKFLOW_ALTERNATIVES: int = 5
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Feature Flags
    ENABLE_MULTI_TENANT: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_RATE_LIMITING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Singleton instance
settings = get_settings()

