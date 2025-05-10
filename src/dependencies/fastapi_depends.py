from collections.abc import AsyncGenerator
from typing import Annotated

from asyncpg import Connection
from fastapi import Depends
from openai import OpenAI

from src.application.ai_support_manager import AISupportManager
from src.application.interfaces.ai_generation_interface import AIGenerationInterface
from src.application.interfaces.ai_support_interface import AISupportInterface
from src.database.connection import get_pool
from src.infrastructure.ai_generation_repository import (
    AIGenerationRepository,
    get_ai_client,
)
from src.infrastructure.ai_support_repository import AISupportRepository


async def get_connection_dependency() -> AsyncGenerator[Connection, None]:
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


def get_ai_support_repository_dependency(
    connection: Annotated[Connection, Depends(get_connection_dependency)],
) -> AISupportInterface:
    return AISupportRepository(connection)


def get_ai_generation_repository_dependency(
    client: Annotated[OpenAI, Depends(get_ai_client)],
) -> AIGenerationInterface:
    return AIGenerationRepository(client=client)


def get_ai_support_manager_dependency(
    ai_support_repository: Annotated[
        AISupportInterface, Depends(get_ai_support_repository_dependency)
    ],
    ai_generation_repository: Annotated[
        AIGenerationInterface, Depends(get_ai_generation_repository_dependency)
    ],
) -> AISupportManager:
    return AISupportManager(
        ai_support_repository=ai_support_repository,
        ai_generation_repository=ai_generation_repository,
    )
