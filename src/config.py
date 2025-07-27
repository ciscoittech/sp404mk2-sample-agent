"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Configuration
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key for AI models"
    )
    
    # Turso Database Configuration
    turso_url: str = Field(
        default="",
        description="Turso database URL (libsql://...)"
    )
    turso_token: str = Field(
        default="",
        description="Turso authentication token"
    )
    
    # GitHub Configuration
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub personal access token (optional if using gh CLI)"
    )
    
    # Agent Configuration
    agent_log_level: str = Field(
        default="INFO",
        description="Logging level for agents"
    )
    agent_max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed operations"
    )
    agent_timeout_seconds: int = Field(
        default=300,
        description="Timeout for agent operations in seconds"
    )
    
    # File Paths
    download_path: Path = Field(
        default=Path("./downloads"),
        description="Path for downloaded samples"
    )
    sample_path: Path = Field(
        default=Path("./samples"),
        description="Path for organized samples"
    )
    review_queue_path: Path = Field(
        default=Path("./review_queue"),
        description="Path for review queue files"
    )
    
    # Audio Processing
    default_sample_rate: int = Field(
        default=44100,
        description="Default sample rate for audio files"
    )
    default_bit_depth: int = Field(
        default=16,
        description="Default bit depth for audio files"
    )
    max_download_size_mb: int = Field(
        default=100,
        description="Maximum file size to download in MB"
    )
    
    # Cost Limits
    daily_token_limit: int = Field(
        default=100000,
        description="Daily token usage limit"
    )
    cost_alert_threshold_usd: float = Field(
        default=5.00,
        description="Cost threshold for alerts in USD"
    )
    
    # Model Configuration
    architect_model: str = Field(
        default="deepseek/deepseek-r1",
        description="Model for Architect Agent"
    )
    coder_models: list[str] = Field(
        default=["deepseek/deepseek-v3", "qwen/qwen3-coder"],
        description="Models for Coder Agent (in priority order)"
    )
    collector_model: str = Field(
        default="google/gemini-flash-2.0",
        description="Model for Collector Agent"
    )
    
    # Model Parameters
    model_temperature: float = Field(
        default=0.5,
        ge=0.0,
        le=2.0,
        description="Default temperature for AI models"
    )
    model_max_tokens: int = Field(
        default=4000,
        description="Default max tokens for AI responses"
    )
    
    @field_validator("turso_url")
    @classmethod
    def validate_turso_url(cls, v: str) -> str:
        """Validate Turso URL format."""
        if v and not v.startswith("libsql://"):
            raise ValueError("Turso URL must start with 'libsql://'")
        return v
    
    @field_validator("agent_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for path in [self.download_path, self.sample_path, self.review_queue_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_bpm_folder(self, bpm: int) -> Path:
        """Get the appropriate BPM folder for a given tempo."""
        if bpm < 80:
            folder_name = "under-80bpm"
        elif bpm < 90:
            folder_name = "80-89bpm"
        elif bpm < 100:
            folder_name = "90-99bpm"
        elif bpm < 110:
            folder_name = "100-109bpm"
        elif bpm < 120:
            folder_name = "110-119bpm"
        elif bpm < 130:
            folder_name = "120-129bpm"
        else:
            folder_name = "over-130bpm"
        
        folder_path = self.sample_path / "organized-by-bpm" / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path


# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()