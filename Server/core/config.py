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
    
    # Azure Cache for Redis Configuration
    # Format: redis://[:password]@host:port/db or rediss://[:password]@host:port/db (SSL)
    # Example Azure: rediss://:password@your-cache.redis.cache.windows.net:6380/0
    REDIS_URL: Optional[str] = None
    REDIS_HOST: Optional[str] = None  # Alternative: specify host/port separately
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = True  # Azure Cache for Redis uses SSL by default
    REDIS_DB: int = 0
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default TTL
    CACHE_ENABLED: bool = True  # Master switch for caching
    
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
    
    def get_redis_url(self) -> Optional[str]:
        """Build Redis URL from components if REDIS_URL not provided"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        if self.REDIS_HOST and self.REDIS_PASSWORD:
            protocol = "rediss" if self.REDIS_SSL else "redis"
            return f"{protocol}://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        
        return None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Singleton instance
settings = get_settings()
