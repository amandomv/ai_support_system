from abc import ABC, abstractmethod

from src.application.interfaces.ai_support_interface import UserQueryHistory
from src.types.documents import FaqDocument
from src.types.embeddings import EmbeddingResponse


class AIGenerationInterface(ABC):
    """
    Interface for AI-related operations.

    This interface defines the contract for AI operations, specifically for generating
    embeddings using OpenAI's API. The implementation should use the recommended
    text-embedding-3-small model and handle errors appropriately.
    """

    @abstractmethod
    async def generate_summary(self, text: str) -> str:
        """
        Generate a concise summary of the given text using OpenAI's API.

        Args:
            text: The text to summarize

        Returns:
            str: A concise summary of the input text

        Raises:
            Exception: If there's an error during the summary generation process
        """
        ...

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

    @abstractmethod
    async def generate_response(
        self, query: str, context_docs: list[FaqDocument]
    ) -> tuple[str, list[FaqDocument]]:
        """
        Generate a response to a user query using the provided context documents.

        Args:
            query: The user's question or query
            context_docs: List of FAQ documents to use as context

        Returns:
            Tuple containing:
                - str: The generated response
                - list[FaqDocument]: List of documents used in the response
                    (empty list if no documents were relevant)

        Raises:
            Exception: If there's an error during the response generation process
        """
        ...

    @abstractmethod
    async def get_recommendations(
        self,
        user_history: list[UserQueryHistory],
        max_recommendations: int = 5,
    ) -> str:
        """
        Generate personalized recommendations based on user's query history.

        Args:
            user_history: List of user's previous queries and responses
            max_recommendations: Maximum number of recommendations to return

        Returns:
            str: Raw text containing recommendations in the format:
                - [document_id]: [explanation]
                - [document_id]: [explanation]
                ...

        Raises:
            Exception: If there's an error generating recommendations
        """
        ...
