import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Nexarch"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./nexarch.db"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2025-01-01-preview"
    
    # Metrics thresholds
    HIGH_LATENCY_THRESHOLD_MS: int = 1000
    HIGH_ERROR_RATE_THRESHOLD: float = 0.05
    MAX_SYNC_CHAIN_DEPTH: int = 5
    MAX_FAN_OUT: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
