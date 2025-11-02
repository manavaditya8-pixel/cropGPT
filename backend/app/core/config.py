"""
Application Configuration Settings
Centralized configuration management for CropGPT backend
"""

import os
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application Settings
    APP_NAME: str = "CropGPT Farmer Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = "postgresql://cropgpt_user:secure_password@localhost:5432/cropgpt"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # API Keys (to be set via environment variables)
    OPENWEATHER_API_KEY: Optional[str] = None
    AGMARKNET_API_KEY: Optional[str] = None
    DIGITAL_INDIA_API_KEY: Optional[str] = None

    # LLM Configuration
    HUGGINGFACE_TOKEN: Optional[str] = None
    MODEL_PATH: str = "/app/models/finetuned_llama2"
    MODEL_NAME: str = "meta-llama/Llama-2-7B-chat-hf"

    # External API URLs
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    AGMARKNET_BASE_URL: str = "https://agmarknet.gov.in/api"
    DIGITAL_INDIA_BASE_URL: str = "https://api.digitalindia.gov.in"

    # Jharkhand Coordinates for Weather
    RANCHI_LATITUDE: float = 23.3441
    RANCHI_LONGITUDE: float = 85.3096

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Cache Settings
    CACHE_DURATION_PRICES: int = 1800  # 30 minutes
    CACHE_DURATION_WEATHER: int = 900   # 15 minutes
    CACHE_DURATION_SCHEMES: int = 86400  # 24 hours

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi"]
    DEFAULT_LANGUAGE: str = "en"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Environment-specific overrides
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
elif settings.ENVIRONMENT == "testing":
    settings.DATABASE_URL = "sqlite:///./test.db"
    settings.REDIS_URL = "redis://localhost:6379/1"