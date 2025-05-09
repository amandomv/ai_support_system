from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asyncpg import Connection, Pool, create_pool

from src.config.settings import get_settings

pool_singleton: dict[str, Pool] = {}
DEFAULT_CONNECTION_NAME: str = "default_connection"


async def get_pool(connection_name: str = DEFAULT_CONNECTION_NAME) -> Pool:
    """
    Get or create the database connection pool.
    This is a singleton pattern implementation.
    """
    pool = pool_singleton.get(connection_name)
    if pool is None:
        settings = get_settings()
        pool = await create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=5,
            max_size=20,
        )
        pool_singleton[connection_name] = pool
    return pool


@asynccontextmanager
async def get_connection() -> AsyncGenerator[Connection, None]:
    """
    Get a database connection from the pool.
    This is a context manager that will automatically release the connection back to the pool.
    """
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


async def close_pool(connection_name: str = DEFAULT_CONNECTION_NAME) -> None:
    """
    Close the database connection pool.
    This should be called when the application is shutting down.
    """
    pool = pool_singleton.get(connection_name)
    if pool:
        await pool.close()
        await pool_singleton.pop(connection_name)
