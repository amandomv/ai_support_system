import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class handles all configuration settings for the application,
    including database and OpenAI credentials. It uses pydantic for
    validation and type checking.
    """

    # Database settings
    POSTGRES_HOST: str = Field(description="PostgreSQL host")
    POSTGRES_PORT: int = Field(description="PostgreSQL port")
    POSTGRES_USER: str = Field(description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(description="PostgreSQL password")
    POSTGRES_DB: str = Field(description="PostgreSQL database name")

    # OpenAI settings
    OPENAI_API_KEY: str = Field(description="OpenAI API key")

    # Optional settings with defaults
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="forbid"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: The application settings instance.

    Note:
        This function is cached to avoid reloading settings on every call.
        The settings are loaded from environment variables and .env file.
    """
    logger = logging.getLogger(__name__)
    logger.info("Loading settings from .env file")
    settings = Settings()  # pyright: ignore
    logger.info("Settings loaded successfully")
    return settings
