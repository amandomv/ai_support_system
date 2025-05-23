from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from src.types.documents import FaqDocument


@dataclass
class UserResponse:
    """Model for storing user questions and AI responses."""

    user_id: int
    user_question: str
    question_embedding: list[float]
    response: str
    response_embedding: list[float]


@dataclass
class UserQueryHistory:
    """Lightweight model for user query history."""

    user_id: int
    user_question: str
    response: str
    created_at: datetime


class AISupportInterface(ABC):
    """
    Interface for AI support operations.

    This interface defines the contract for AI support operations, specifically for
    retrieving FAQ documents based on semantic similarity to a query and storing
    user interactions.
    """

    @abstractmethod
    async def get_faq_documents_by_similarity(
        self,
        embeddings: list[float],
        max_documents: int = 5,
        i_am_a_developer: bool = False,
    ) -> list[FaqDocument]:
        """
        Retrieve FAQ documents that are semantically similar to the provided embeddings.

        Args:
            embeddings: List of float values representing the query embedding
            max_documents: Maximum number of documents to return (default: 5)
            i_am_a_developer: If True, include technical documents in the results

        Returns:
            List of FaqDocument objects ordered by similarity to the query

        Raises:
            ValueError: If embeddings list is empty or invalid
            DatabaseError: If there's an error accessing the database
            Exception: For any other unexpected errors during document retrieval
        """

    @abstractmethod
    async def save_user_response(self, user_response: UserResponse) -> None:
        """
        Save a user question and its AI response to the database.

        Args:
            user_response: UserResponse object containing:
                - user_id: The ID of the user making the query
                - user_question: The question asked by the user
                - question_embedding: Vector embedding of the user question
                - response: The AI-generated response
                - response_embedding: Vector embedding of the AI response

        Raises:
            ValueError: If any of the required fields are invalid
            DatabaseError: If there's an error saving to the database
            Exception: For any other unexpected errors during save operation
        """

    @abstractmethod
    async def get_user_query_history(self, user_id: int) -> list[UserQueryHistory]:
        """
        Retrieve the user's query history.

        Args:
            user_id: The ID of the user

        Returns:
            List of UserQueryHistory objects representing the user's query history,
            ordered by most recent first

        Raises:
            ValueError: If user_id is invalid
            DatabaseError: If there's an error accessing the database
        """

    @abstractmethod
    async def get_faq_document(self, document_id: int) -> FaqDocument | None:
        """
        Get a FAQ document by its ID.

        Args:
            document_id: The ID of the FAQ document to retrieve

        Returns:
            FaqDocument if found, None otherwise
        """
