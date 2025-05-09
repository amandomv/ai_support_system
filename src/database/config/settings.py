import os
from functools import cache

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_host: str = os.getenv("POSTGRES_HOST", "localhost")
    db_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user: str = os.getenv("POSTGRES_USER", "postgres")
    db_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name: str = os.getenv("POSTGRES_DB", "ai_support_system")


_settings: DatabaseSettings | None = None


@cache
def get_settings() -> DatabaseSettings:
    """
    Get the database settings singleton instance.
    """
    return DatabaseSettings()
