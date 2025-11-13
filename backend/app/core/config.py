"""
Application configuration using Pydantic Settings
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    PROJECT_NAME: str = "SP404MK2 Sample Manager API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sp404_samples.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_TYPES: List[str] = [
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/flac",
        "audio/aiff",
        "audio/x-aiff",
        "audio/ogg",
        "audio/vorbis"
    ]
    
    # Redis (for caching and queues)
    REDIS_URL: Optional[str] = None
    
    # External APIs
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Additional settings from .env
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_AUDIO_EXTENSIONS: str = ".wav,.mp3,.flac,.ogg,.m4a,.aiff"
    CHAT_MODEL: str = "google/gemma-3-27b-it"
    COLLECTOR_MODEL: str = "qwen/qwen3-235b-a22b-2507"
    DEBUG: bool = False

    # OpenRouter API Usage Tracking & Cost Management
    model_pricing: dict = {
        "google/gemma-3-27b-it": {
            "input": 0.09 / 1_000_000,   # $0.09 per 1M input tokens
            "output": 0.16 / 1_000_000   # $0.16 per 1M output tokens
        },
        "qwen/qwen3-235b-a22b-2507": {
            "input": 0.20 / 1_000_000,   # $0.20 per 1M input tokens
            "output": 0.60 / 1_000_000   # $0.60 per 1M output tokens
        },
        "qwen/qwen3-235b-a22b-2507:free": {
            "input": 0.0,                # Free tier
            "output": 0.0
        },
        "deepseek/deepseek-r1": {
            "input": 0.10 / 1_000_000,
            "output": 0.40 / 1_000_000
        },
        "deepseek/deepseek-v3": {
            "input": 0.27 / 1_000_000,
            "output": 1.10 / 1_000_000
        },
        "qwen/qwen3-coder": {
            "input": 0.15 / 1_000_000,
            "output": 0.50 / 1_000_000
        }
    }

    # Budget Limits
    monthly_budget_usd: float = 10.0
    daily_token_limit: int = 100_000
    budget_alert_threshold: float = 0.8

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


settings = Settings()