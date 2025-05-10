from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.ai_support_manager import AISupportManager
from src.infrastructure.ai_generation_repository import AIGenerationRepository
from src.infrastructure.ai_support_repository import AISupportRepository
from src.types.documents import FaqCategory, FaqDocument
from src.types.embeddings import Embedding, EmbeddingResponse
from src.types.user import User


@pytest.fixture
def mock_ai_repository() -> AsyncMock:
    """Create a mock AI repository."""
    return AsyncMock(spec=AIGenerationRepository)


@pytest.fixture
def mock_ai_support_repository() -> AsyncMock:
    """Create a mock AI support repository."""
    return AsyncMock(spec=AISupportRepository)


@pytest.fixture
def ai_support_manager(
    mock_ai_repository: AsyncMock, mock_ai_support_repository: AsyncMock
) -> AISupportManager:
    """Create an AISupportManager instance with mock repositories."""
    return AISupportManager(mock_ai_repository, mock_ai_support_repository)


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
        user_name="Test User",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_faq_documents() -> list[FaqDocument]:
    """Create sample FAQ documents for testing."""
    return [
        FaqDocument(
            id=1,
            title="Test Document 1",
            link="http://test1.com",
            text="This is test document 1",
            category=FaqCategory.PLATFORM_OVERVIEW,
            embedding=[0.1] * 1536,  # OpenAI embeddings are 1536 dimensions
        ),
        FaqDocument(
            id=2,
            title="Test Document 2",
            link="http://test2.com",
            text="This is test document 2",
            category=FaqCategory.PLATFORM_OVERVIEW,
            embedding=[0.2] * 1536,  # OpenAI embeddings are 1536 dimensions
        ),
    ]


@pytest.mark.asyncio
async def test_generate_ai_support_response(
    ai_support_manager: AISupportManager,
    mock_ai_repository: AsyncMock,
    mock_ai_support_repository: AsyncMock,
    sample_user: User,
    sample_faq_documents: list[FaqDocument],
) -> None:
    """Test generate_ai_support_response method."""
    # Arrange
    test_query = "Test question"
    test_embedding = [0.1] * 1536  # OpenAI embeddings are 1536 dimensions
    test_response = "Test response"
    test_used_documents = [
        sample_faq_documents[0]
    ]  # Use the first document from sample_faq_documents

    mock_ai_repository.generate_embeddings.return_value = EmbeddingResponse(
        embedding=Embedding(vector=test_embedding),
        model="text-embedding-3-small",
        usage={"prompt_tokens": 2, "total_tokens": 2},
    )
    mock_ai_support_repository.get_faq_documents_by_similarity.return_value = (
        sample_faq_documents
    )
    mock_ai_repository.generate_response.return_value = (
        test_response,
        test_used_documents,
    )

    # Act
    result = await ai_support_manager.generate_ai_support_response(
        test_query, sample_user.id
    )

    # Assert
    assert result.response == test_response
    assert len(result.docs_used) == 1
    assert result.docs_used[0].title == "Test Document 1"
    assert result.docs_used[0].link == "http://test1.com"
    assert (
        mock_ai_repository.generate_embeddings.call_count == 2
    )  # Called for query and response
    mock_ai_repository.generate_response.assert_called_once_with(
        test_query, sample_faq_documents
    )
    mock_ai_support_repository.save_user_response.assert_called_once()
    # Verify the UserResponse object passed to save_user_response
    call_args = mock_ai_support_repository.save_user_response.call_args[0][0]
    assert call_args.user_id == sample_user.id
    assert call_args.user_question == test_query
    assert call_args.question_embedding == test_embedding
    assert call_args.response == test_response
    assert call_args.response_embedding == test_embedding


def test_create_support_response() -> None:
    """Test _create_support_response static method."""
    # Arrange
    test_response = "Test response"
    test_documents = [
        FaqDocument(
            id=1,
            title="Test Document 1",
            link="http://test1.com",
            text="This is test document 1",
            category=FaqCategory.PLATFORM_OVERVIEW,
            embedding=[0.1] * 1536,  # OpenAI embeddings are 1536 dimensions
        )
    ]

    # Act
    result = AISupportManager._create_support_response(test_response, test_documents)

    # Assert
    assert result.response == test_response
    assert len(result.docs_used) == 1
    assert result.docs_used[0].title == "Test Document 1"


@pytest.mark.asyncio
async def test_generate_response_with_context(
    ai_support_manager: AISupportManager,
    mock_ai_repository: AsyncMock,
    sample_faq_documents: list[FaqDocument],
) -> None:
    """Test _generate_response_with_context method."""
    # Arrange
    test_query = "Test question"
    test_response = "Test response"
    test_used_documents = ["Test Document 1"]

    mock_ai_repository.generate_response.return_value = (
        test_response,
        test_used_documents,
    )

    # Act
    result = await ai_support_manager._generate_response_with_context(
        test_query, sample_faq_documents
    )

    # Assert
    assert result[0] == test_response
    assert result[1] == test_used_documents
    mock_ai_repository.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_save_user_interaction(
    ai_support_manager: AISupportManager,
    mock_ai_support_repository: AsyncMock,
    sample_user: User,
) -> None:
    """Test _save_user_interaction method."""
    # Arrange
    test_query = "Test question"
    test_embedding = [0.1, 0.2, 0.3]
    test_response = "Test response"

    # Act
    await ai_support_manager._save_user_interaction(
        sample_user.id, test_query, test_embedding, test_response
    )

    # Assert
    mock_ai_support_repository.save_user_response.assert_called_once()


@pytest.mark.asyncio
async def test_generate_ai_support_response_error_handling(
    ai_support_manager: AISupportManager,
    mock_ai_repository: AsyncMock,
    sample_user: User,
) -> None:
    """Test error handling in generate_ai_support_response method."""
    # Arrange
    mock_ai_repository.generate_embeddings.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_support_manager.generate_ai_support_response(
            "Test question", sample_user.id
        )
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
async def test_generate_response_with_context_error_handling(
    ai_support_manager: AISupportManager,
    mock_ai_repository: AsyncMock,
    sample_faq_documents: list[FaqDocument],
) -> None:
    """Test error handling in _generate_response_with_context method."""
    # Arrange
    mock_ai_repository.generate_response.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_support_manager._generate_response_with_context(
            "Test question", sample_faq_documents
        )
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
async def test_save_user_interaction_error_handling(
    ai_support_manager: AISupportManager,
    mock_ai_support_repository: AsyncMock,
    sample_user: User,
) -> None:
    """Test error handling in _save_user_interaction method."""
    # Arrange
    mock_ai_support_repository.save_user_response.side_effect = Exception(
        "Database Error"
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_support_manager._save_user_interaction(
            sample_user.id, "Test question", [0.1, 0.2, 0.3], "Test response"
        )
    assert str(exc_info.value) == "Database Error"
