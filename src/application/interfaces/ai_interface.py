from abc import ABC, abstractmethod

from src.types.embeddings import EmbeddingResponse


class AIInterface(ABC):
    """
    Interface for AI-related operations.

    This interface defines the contract for AI operations, specifically for generating
    embeddings using OpenAI's API. The implementation should use the recommended
    text-embedding-3-small model and handle errors appropriately.
    """

    @abstractmethod
    async def generate_embeddings(self, text: str) -> EmbeddingResponse:
        """
        Generate embeddings for the given text using OpenAI's API.

        Args:
            text: The text to generate embeddings for

        Returns:
            EmbeddingResponse containing:
                - embedding: The generated embedding vector
                - model: The model used for generation
                - usage: Dictionary with token usage statistics
                    - prompt_tokens: Number of tokens in the input
                    - total_tokens: Total tokens used in the request

        Raises:
            Exception: If there's an error during the embedding generation process
        """
        ...
