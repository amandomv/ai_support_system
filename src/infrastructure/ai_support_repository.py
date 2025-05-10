import json
import logging
from typing import Any

from asyncpg import Connection

from src.application.interfaces.ai_support_interface import (
    AISupportInterface,
    UserResponse,
)
from src.types.documents import FaqDocument


class AISupportRepository(AISupportInterface):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _format_embeddings(embeddings: list[float]) -> str:
        """Format embeddings list as a PostgreSQL array string."""
        return f"[{', '.join(map(str, embeddings))}]"

    @staticmethod
    def _convert_to_faq_document(doc: dict[str, Any]) -> FaqDocument:
        """Convert a database record to a FaqDocument instance."""
        doc_dict = dict(doc)
        doc_dict["embedding"] = AISupportRepository._parse_embedding(
            doc_dict["embedding"]
        )
        return FaqDocument(**doc_dict)

    @staticmethod
    def _parse_embedding(embedding: str | list[float]) -> list[float]:
        """Parse embedding from database format to list of floats."""
        if isinstance(embedding, str):
            try:
                return json.loads(embedding)
            except json.JSONDecodeError:
                return [float(x.strip()) for x in embedding.strip("[]").split(",")]
        return embedding

    async def get_faq_documents_by_similarity(
        self, embeddings: list[float], max_documents: int = 5
    ) -> list[FaqDocument]:
        query = """
        SELECT * FROM platform_information.faq_documents
        ORDER BY embedding <> $1
        LIMIT $2
        """
        faq_similar_documents = await self.connection.fetch(
            query, self._format_embeddings(embeddings), max_documents
        )

        return [self._convert_to_faq_document(doc) for doc in faq_similar_documents]

    async def save_user_response(self, user_response: UserResponse) -> None:
        """
        Save a user question and its AI response to the database.

        Args:
            user_response: UserResponse object containing the interaction data

        Raises:
            ValueError: If any of the required fields are invalid
            DatabaseError: If there's an error saving to the database
            Exception: For any other unexpected errors during save operation
        """
        try:
            query = """
            INSERT INTO user_management.user_response
            (user_id, user_question, question_embedding, response, response_embedding)
            VALUES ($1, $2, $3, $4, $5)
            """

            await self.connection.execute(
                query,
                user_response.user_id,
                user_response.user_question,
                self._format_embeddings(user_response.question_embedding),
                user_response.response,
                self._format_embeddings(user_response.response_embedding),
            )
            self.logger.debug(f"Saved user response for user {user_response.user_id}")
        except Exception as e:
            self.logger.error(f"Error saving user response: {str(e)}")
            raise
