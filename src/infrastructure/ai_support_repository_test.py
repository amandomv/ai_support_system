import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.interfaces.ai_support_interface import UserResponse
from src.infrastructure.ai_support_repository import AISupportRepository
from src.types.documents import FaqCategory, FaqDocument
from src.types.user import User


@pytest.fixture
def mock_db() -> AsyncMock:
    """Create a mock database connection."""
    return AsyncMock()


@pytest.fixture
def ai_support_repository(mock_db: AsyncMock) -> AISupportRepository:
    """Create an AISupportRepository instance with a mock database."""
    return AISupportRepository(mock_db)


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
            embedding=[0.1, 0.2, 0.3],
        ),
        FaqDocument(
            id=2,
            title="Test Document 2",
            link="http://test2.com",
            text="This is test document 2",
            category=FaqCategory.PLATFORM_OVERVIEW,
            embedding=[0.4, 0.5, 0.6],
        ),
    ]


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


@pytest.mark.asyncio
async def test_save_user_response(
    ai_support_repository: AISupportRepository, mock_db: AsyncMock, sample_user: User
) -> None:
    """Test save_user_response method."""
    # Arrange
    test_query = "Test question"
    test_embedding = [0.1, 0.2, 0.3]
    test_response = "Test response"
    test_response_embedding = [0.4, 0.5, 0.6]

    user_response = UserResponse(
        user_id=sample_user.id,
        user_question=test_query,
        question_embedding=test_embedding,
        response=test_response,
        response_embedding=test_response_embedding,
    )

    # Act
    await ai_support_repository.save_user_response(user_response)

    # Assert
    mock_db.execute.assert_called_once()


def test_format_embeddings() -> None:
    """Test _format_embeddings static method."""
    # Arrange
    test_embedding = [0.1, 0.2, 0.3]

    # Act
    result = AISupportRepository._format_embeddings(test_embedding)

    # Assert
    assert result == "[0.1, 0.2, 0.3]"


def test_convert_to_faq_document() -> None:
    """Test _convert_to_faq_document static method."""
    # Arrange
    test_doc = {
        "id": 1,
        "title": "Test Document",
        "link": "http://test.com",
        "text": "Test text",
        "category": "platform_overview",
        "embedding": json.dumps([0.1, 0.2, 0.3]),
    }

    # Act
    result = AISupportRepository._convert_to_faq_document(test_doc)

    # Assert
    assert isinstance(result, FaqDocument)
    assert result.title == "Test Document"
    assert result.embedding == [0.1, 0.2, 0.3]


def test_parse_embedding_string() -> None:
    """Test _parse_embedding static method with string input."""
    # Arrange
    test_embedding = "[0.1, 0.2, 0.3]"

    # Act
    result = AISupportRepository._parse_embedding(test_embedding)

    # Assert
    assert result == [0.1, 0.2, 0.3]


def test_parse_embedding_list() -> None:
    """Test _parse_embedding static method with list input."""
    # Arrange
    test_embedding = [0.1, 0.2, 0.3]

    # Act
    result = AISupportRepository._parse_embedding(test_embedding)

    # Assert
    assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_save_user_response_error_handling(
    ai_support_repository: AISupportRepository, mock_db: AsyncMock, sample_user: User
) -> None:
    """Test error handling in save_user_response method."""
    # Arrange
    mock_db.execute.side_effect = Exception("Database Error")
    user_response = UserResponse(
        user_id=sample_user.id,
        user_question="Test question",
        question_embedding=[0.1, 0.2, 0.3],
        response="Test response",
        response_embedding=[0.4, 0.5, 0.6],
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_support_repository.save_user_response(user_response)
    assert str(exc_info.value) == "Database Error"
