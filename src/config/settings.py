import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "forbid",
    }

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create settings instance from environment variables.

        Returns:
            Settings: The application settings instance.
        """
        return cls(
            POSTGRES_HOST=os.getenv("POSTGRES_HOST", ""),
            POSTGRES_PORT=int(os.getenv("POSTGRES_PORT", "5432")),
            POSTGRES_USER=os.getenv("POSTGRES_USER", ""),
            POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", ""),
            POSTGRES_DB=os.getenv("POSTGRES_DB", ""),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
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
    return Settings.from_env()
