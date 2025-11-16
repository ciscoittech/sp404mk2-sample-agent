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
    # Default to PostgreSQL (can be overridden via .env for local SQLite development)
    DATABASE_URL: str = "postgresql+asyncpg://sp404_user:changeme@localhost:5432/sp404_samples"
    
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
    APP_URL: str = "http://localhost:8100"

    # Environment
    ENVIRONMENT: str = "development"
    
    # Additional settings from .env
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_AUDIO_EXTENSIONS: str = ".wav,.mp3,.flac,.ogg,.m4a,.aiff"
    CHAT_MODEL: str = "google/gemma-3-27b-it"
    COLLECTOR_MODEL: str = "qwen/qwen3-235b-a22b-2507"
    DEBUG: bool = False

    # Audio Analysis Settings
    USE_ESSENTIA: bool = True
    """Master switch to enable/disable Essentia audio analysis.

    When True and Essentia is available, Essentia will be used for BPM detection
    and genre classification (if enabled). Falls back to librosa if Essentia fails
    or is unavailable.

    Set to False to always use librosa, useful for:
    - Development environments without Essentia installed
    - Debugging librosa-specific behavior
    - Systems where Essentia installation is problematic

    Default: True (use Essentia when available)
    """

    ENABLE_GENRE_CLASSIFICATION: bool = False
    """Enable/disable Essentia genre classification feature.

    Genre classification requires:
    - Essentia to be installed and available
    - Pre-trained TensorFlow models to be downloaded (~150MB)
    - Model files in backend/models/essentia/

    Set to False to:
    - Skip genre classification (BPM only)
    - Avoid model compatibility issues
    - Reduce memory usage during analysis

    Note: Currently disabled by default due to model compatibility issues.
    Will be enabled in future release after TensorFlow compatibility is resolved.

    Default: False (genre classification disabled)
    """

    ESSENTIA_BPM_METHOD: str = "multifeature"
    """BPM detection method to use when Essentia is enabled.

    Available methods:
    - "multifeature": Most accurate, slower (recommended for samples <30s)
    - "degara": Fast, good accuracy (recommended for samples >=30s)
    - "percival": Alternative algorithm, balanced speed/accuracy

    The service will auto-select the best method based on sample duration
    if not explicitly overridden.

    Default: "multifeature"
    """

    AUDIO_ANALYSIS_TIMEOUT: int = 30
    """Maximum time (in seconds) to wait for audio analysis to complete.

    Prevents hanging on corrupted files or extremely long samples.
    If analysis exceeds this timeout, it will be cancelled and an error returned.

    Recommended values:
    - Development: 30 seconds
    - Production: 60 seconds (for large files)
    - Batch processing: 120 seconds

    Default: 30 seconds
    """

    # OpenRouter API Usage Tracking & Cost Management
    model_pricing: dict = {
        "google/gemma-3-27b-it": {
            "input": 0.09 / 1_000_000,   # $0.09 per 1M input tokens
            "output": 0.16 / 1_000_000   # $0.16 per 1M output tokens
        },
        "qwen/qwen-2.5-7b-instruct": {
            "input": 0.06 / 1_000_000,   # $0.06 per 1M input tokens (7B instruct model)
            "output": 0.12 / 1_000_000   # $0.12 per 1M output tokens
        },
        "qwen/qwen3-7b-it": {
            "input": 0.06 / 1_000_000,   # Alias for qwen-2.5-7b-instruct
            "output": 0.12 / 1_000_000
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