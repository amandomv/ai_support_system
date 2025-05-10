from abc import ABC, abstractmethod

from src.types.documents import FaqDocument


class AISupportInterface(ABC):
    """
    Interface for AI support operations.

    This interface defines the contract for AI support operations, specifically for
    retrieving FAQ documents based on semantic similarity to a query.
    """

    @abstractmethod
    async def get_faq_documents_by_similarity(
        self, embeddings: list[float], max_documents: int = 5
    ) -> list[FaqDocument]:
        """
        Retrieve FAQ documents that are semantically similar to the provided embeddings.

        Args:
            embeddings: List of float values representing the query embedding
            max_documents: Maximum number of documents to return (default: 5)

        Returns:
            List of FaqDocument objects ordered by similarity to the query

        Raises:
            ValueError: If embeddings list is empty or invalid
            DatabaseError: If there's an error accessing the database
            Exception: For any other unexpected errors during document retrieval
        """
