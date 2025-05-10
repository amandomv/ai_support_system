from unittest.mock import AsyncMock

import pytest

from src.application.dump_data_manager import DumpDataManager
from src.infrastructure.ai_generation_repository import AIGenerationRepository
from src.infrastructure.dump_data_repository import DumpDataRepository
from src.types.embeddings import Embedding, EmbeddingResponse
from src.types.user import User


@pytest.fixture
def mock_dump_data_repository() -> AsyncMock:
    """Create a mock dump data repository."""
    return AsyncMock(spec=DumpDataRepository)


@pytest.fixture
def mock_ai_repository() -> AsyncMock:
    """Create a mock AI repository."""
    return AsyncMock(spec=AIGenerationRepository)


@pytest.fixture
def dump_data_manager(
    mock_dump_data_repository: AsyncMock, mock_ai_repository: AsyncMock
) -> DumpDataManager:
    """Create a DumpDataManager instance with mock repositories."""
    return DumpDataManager(mock_dump_data_repository, mock_ai_repository)


@pytest.fixture
def sample_base_data() -> list[dict[str, str]]:
    """Create sample base data for testing."""
    return [
        {
            "title": "Test Document 1",
            "link": "http://test1.com",
            "text": "This is test document 1",
            "category": "platform_overview",
        },
        {
            "title": "Test Document 2",
            "link": "http://test2.com",
            "text": "This is test document 2",
            "category": "platform_overview",
        },
    ]


@pytest.mark.asyncio
async def test_dump_data(
    dump_data_manager: DumpDataManager,
    mock_dump_data_repository: AsyncMock,
    mock_ai_repository: AsyncMock,
    sample_base_data: list[dict[str, str]],
) -> None:
    """Test dump_data method."""
    # Arrange
    mock_ai_repository.generate_summary.return_value = "Test summary"
    mock_ai_repository.generate_embeddings.return_value = EmbeddingResponse(
        embedding=Embedding(
            vector=[0.1] * 1536
        ),  # OpenAI embeddings are 1536 dimensions
        model="text-embedding-3-small",
        usage={"prompt_tokens": 2, "total_tokens": 2},
    )

    # Act
    await dump_data_manager.dump_data(sample_base_data)

    # Assert
    assert mock_ai_repository.generate_summary.call_count == 2
    assert mock_ai_repository.generate_embeddings.call_count == 2
    mock_dump_data_repository.dump_faq_documents.assert_called_once()


@pytest.mark.asyncio
async def test_create_test_user(
    dump_data_manager: DumpDataManager,
    mock_dump_data_repository: AsyncMock,
) -> None:
    """Test create_test_user method."""
    # Act
    await dump_data_manager.create_test_user()

    # Assert
    mock_dump_data_repository.dump_user_data.assert_called_once()


def test_create_test_user_static() -> None:
    """Test create_test_user method."""
    # Act
    result = DumpDataManager._create_test_user()

    # Assert
    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.user_name == "Test User"


@pytest.mark.asyncio
async def test_dump_data_error_handling(
    dump_data_manager: DumpDataManager,
    mock_ai_repository: AsyncMock,
    sample_base_data: list[dict[str, str]],
) -> None:
    """Test error handling in dump_data method."""
    # Arrange
    mock_ai_repository.generate_embeddings.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await dump_data_manager.dump_data(sample_base_data)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
async def test_create_test_user_error_handling(
    dump_data_manager: DumpDataManager,
    mock_dump_data_repository: AsyncMock,
) -> None:
    """Test error handling in create_test_user method."""
    # Arrange
    mock_dump_data_repository.dump_user_data.side_effect = Exception("Database Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await dump_data_manager.create_test_user()
    assert str(exc_info.value) == "Database Error"
