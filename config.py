import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "collalearn"
    
    # AI Service
    AI_API_KEY: str
    AI_API_URL: str = "https://api.perplexity.ai/chat/completions"
    AI_MODEL: str = "llama-3.1-sonar-small-128k-online"
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7
    
    # Rate Limiting
    AI_CALLS_PER_USER_PER_DAY: int = 50
    
    # Admin Panel
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"
    ADMIN_SECRET_KEY: str = "your-secret-key-change-this"
    ADMIN_PORT: int = 8000
    
    # Application
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()