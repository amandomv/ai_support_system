import json
import logging

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

    async def get_faq_documents_by_similarity(
        self, embeddings: list[float], max_documents: int = 5
    ) -> list[FaqDocument]:
        query = """
        SELECT * FROM platform_information.faq_documents
        ORDER BY embedding <> $1
        LIMIT $2
        """
        faq_similar_documents = await self.connection.fetch(
            query, f"[{', '.join(map(str, embeddings))}]", max_documents
        )

        # Convert the documents and ensure embedding is a list
        documents = []
        for doc in faq_similar_documents:
            doc_dict = dict(doc)
            # Convert embedding string to list if it's a string
            if isinstance(doc_dict["embedding"], str):
                try:
                    doc_dict["embedding"] = json.loads(doc_dict["embedding"])
                except json.JSONDecodeError:
                    # If it's not valid JSON, try to parse it as a comma-separated list
                    doc_dict["embedding"] = [
                        float(x.strip())
                        for x in doc_dict["embedding"].strip("[]").split(",")
                    ]
            documents.append(FaqDocument(**doc_dict))

        return documents

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
                f"[{', '.join(map(str, user_response.question_embedding))}]",
                user_response.response,
                f"[{', '.join(map(str, user_response.response_embedding))}]",
            )
            self.logger.debug(f"Saved user response for user {user_response.user_id}")
        except Exception as e:
            self.logger.error(f"Error saving user response: {str(e)}")
            raise
