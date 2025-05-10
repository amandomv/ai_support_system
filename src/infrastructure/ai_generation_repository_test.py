from unittest.mock import MagicMock

import pytest
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.create_embedding_response import CreateEmbeddingResponse
from openai.types.embedding import Embedding

from src.infrastructure.ai_generation_repository import (
    AIGenerationRepository,
    FormattedResponse,
)
from src.types.documents import FaqCategory, FaqDocument
from src.types.embeddings import EmbeddingResponse


@pytest.fixture
def mock_openai_client() -> OpenAI:
    """Create a mock OpenAI client."""
    client = MagicMock(spec=OpenAI)
    return client


@pytest.fixture
def ai_repository(mock_openai_client: OpenAI) -> AIGenerationRepository:
    """Create an AIGenerationRepository instance with a mock client."""
    return AIGenerationRepository(mock_openai_client)


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


@pytest.mark.asyncio
async def test_generate_embeddings(
    ai_repository: AIGenerationRepository, mock_openai_client: OpenAI
) -> None:
    """Test generate_embeddings method."""
    # Arrange
    test_text = "Test text"
    mock_embedding = [0.1] * 1536  # OpenAI embeddings are 1536 dimensions
    mock_response = CreateEmbeddingResponse(
        data=[Embedding(embedding=mock_embedding, index=0, object="embedding")],
        model="text-embedding-3-small",
        object="list",
        usage={"prompt_tokens": 2, "total_tokens": 2},
    )
    mock_openai_client.embeddings.create.return_value = mock_response

    # Act
    result = await ai_repository.generate_embeddings(test_text)

    # Assert
    assert isinstance(result, EmbeddingResponse)
    assert result.embedding.vector == mock_embedding
    assert result.model == "text-embedding-3-small"
    assert result.usage == {"prompt_tokens": 2, "total_tokens": 2}
    mock_openai_client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small", input=test_text, encoding_format="float"
    )


@pytest.mark.asyncio
async def test_generate_response(
    ai_repository: AIGenerationRepository,
    mock_openai_client: OpenAI,
    sample_faq_documents: list[FaqDocument],
) -> None:
    """Test generate_response method."""
    # Arrange
    test_query = "Test question"
    mock_chat_response = ChatCompletion(
        id="test-id",
        choices=[
            {
                "message": ChatCompletionMessage(
                    content='{"answer": "Test answer", "used_documents": ["Test Document 1"]}',
                    role="assistant",
                ),
                "index": 0,
                "finish_reason": "stop",
            }
        ],
        created=1234567890,
        model="gpt-3.5-turbo",
        object="chat.completion",
    )
    mock_openai_client.chat.completions.create.return_value = mock_chat_response

    # Act
    answer, used_docs = await ai_repository.generate_response(
        test_query, sample_faq_documents
    )

    # Assert
    assert answer == "Test answer"
    assert len(used_docs) == 1
    assert used_docs[0].title == "Test Document 1"
    mock_openai_client.chat.completions.create.assert_called_once()


def test_create_prompt_template() -> None:
    """Test _create_prompt_template static method."""
    # Act
    template = AIGenerationRepository._create_prompt_template()

    # Assert
    assert template is not None
    assert len(template.messages) == 2
    assert (
        template.messages[0].prompt.template
        == """You are a technical support assistant for the Shakers platform.
                Your task is to answer user questions using ONLY the provided context.
                If the answer is not in the context, say you don't have that information.

                Format your response as follows:
                - Start with a clear, concise answer
                - If relevant, provide additional context or examples
                - Keep the tone professional but friendly
                - Do not mention that you are an AI or that you are using context

                {format_instructions}"""
    )
    assert (
        template.messages[1].prompt.template
        == """Context:
                {context}

                User question: {query}"""
    )


def test_prepare_context(sample_faq_documents: list[FaqDocument]) -> None:
    """Test _prepare_context static method."""
    # Act
    context = AIGenerationRepository._prepare_context(sample_faq_documents)

    # Assert
    assert "Test Document 1" in context
    assert "Test Document 2" in context
    assert "This is test document 1" in context
    assert "This is test document 2" in context


def test_get_used_documents(sample_faq_documents: list[FaqDocument]) -> None:
    """Test _get_used_documents static method."""
    # Arrange
    parsed_response = FormattedResponse(
        answer="Test answer",
        used_documents=["Test Document 1"],
    )

    # Act
    used_docs = AIGenerationRepository._get_used_documents(
        parsed_response, sample_faq_documents
    )

    # Assert
    assert len(used_docs) == 1
    assert used_docs[0].title == "Test Document 1"


@pytest.mark.asyncio
async def test_generate_embeddings_error_handling(
    ai_repository: AIGenerationRepository, mock_openai_client: OpenAI
) -> None:
    """Test error handling in generate_embeddings method."""
    # Arrange
    mock_openai_client.embeddings.create.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_repository.generate_embeddings("Test text")
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
async def test_generate_response_error_handling(
    ai_repository: AIGenerationRepository,
    mock_openai_client: OpenAI,
    sample_faq_documents: list[FaqDocument],
) -> None:
    """Test error handling in generate_response method."""
    # Arrange
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ai_repository.generate_response("Test question", sample_faq_documents)
    assert str(exc_info.value) == "API Error"
