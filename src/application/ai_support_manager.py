import logging

from pydantic import BaseModel

from src.application.interfaces.ai_generation_interface import AIGenerationInterface
from src.application.interfaces.ai_support_interface import (
    AISupportInterface,
    UserResponse,
)
from src.infrastructure.prometheus_metrics import (
    track_document_search_time,
    track_embedding_time,
    track_response_time,
)
from src.types.documents import FaqDocument, FaqDocumentBaseData
from src.types.embeddings import EmbeddingResponse
from src.types.recommendations import Recommendation, RecommendationResponse


class SupportResponse(BaseModel):
    """Response model for AI support queries."""

    response: str
    docs_used: list[FaqDocumentBaseData]


class AISupportManager:
    """
    Manager class for AI support operations.

    This class coordinates the interaction between AI generation and support repositories
    to provide comprehensive support responses based on user queries.
    """

    def __init__(
        self,
        ai_generation_repository: AIGenerationInterface,
        ai_support_repository: AISupportInterface,
    ):
        """
        Initialize the AI support manager.

        Args:
            ai_generation_repository: Repository for AI generation operations
            ai_support_repository: Repository for AI support operations
        """
        self.logger = logging.getLogger(__name__)
        self.ai_generation_repository = ai_generation_repository
        self.ai_support_repository = ai_support_repository

    @staticmethod
    def _create_support_response(
        response: str, context_docs: list[FaqDocument]
    ) -> SupportResponse:
        """Create a SupportResponse instance from the response and context documents."""
        return SupportResponse(
            response=response,
            docs_used=[
                FaqDocumentBaseData(title=doc.title, link=doc.link)
                for doc in context_docs
            ],
        )

    async def _generate_response_with_context(
        self, query: str, similar_docs: list[FaqDocument]
    ) -> tuple[str, list[FaqDocument]]:
        """Generate a response using the query and similar documents."""
        response, context_docs = await self.ai_generation_repository.generate_response(
            query, similar_docs
        )
        self.logger.debug(f"Generated response using {len(context_docs)} documents")
        return response, context_docs

    async def _save_user_interaction(
        self,
        user_id: int,
        query: str,
        query_embeddings: list[float],
        response: str,
    ) -> None:
        """Save a user interaction to the database."""
        self.logger.debug("Generated embeddings for response")
        response_embeddings = await self._generate_embeddings(response)

        user_response = UserResponse(
            user_id=user_id,
            user_question=query,
            question_embedding=query_embeddings,
            response=response,
            response_embedding=response_embeddings.embedding.vector,
        )
        await self.ai_support_repository.save_user_response(user_response)
        self.logger.debug("Saved user interaction in database")

    @track_response_time
    async def generate_ai_support_response(
        self, query: str, user_id: int, i_am_a_developer: bool = False
    ) -> SupportResponse:
        """
        Generate an AI support response for a user query.

        Args:
            query: The user's question or query
            user_id: The ID of the user making the query
            i_am_a_developer: If True, include technical documents in the results

        Returns:
            SupportResponse containing the generated response and relevant documents

        Raises:
            Exception: If there's an error during response generation
        """
        try:
            self.logger.info(f"Processing query for user {user_id}: {query[:100]}...")

            # Generate embeddings and find similar documents
            query_embeddings = await self._generate_embeddings(query)
            similar_docs = await self._find_similar_documents(
                query_embeddings.embedding.vector, i_am_a_developer=i_am_a_developer
            )

            # Generate response
            response, context_docs = await self._generate_response_with_context(
                query, similar_docs
            )

            # Save the interaction
            await self._save_user_interaction(
                user_id=user_id,
                query=query,
                query_embeddings=query_embeddings.embedding.vector,
                response=response,
            )

            # Create and return the response
            return self._create_support_response(response, context_docs)

        except Exception as e:
            self.logger.error(f"Error generating support response: {str(e)}")
            raise

    @track_embedding_time
    async def _generate_embeddings(self, query: str) -> EmbeddingResponse:
        """Generate embeddings for the query."""
        return await self.ai_generation_repository.generate_embeddings(query)

    @track_document_search_time
    async def _find_similar_documents(
        self, vector: list[float], i_am_a_developer: bool = False
    ) -> list[FaqDocument]:
        """Find similar documents using the embedding vector."""
        return await self.ai_support_repository.get_faq_documents_by_similarity(
            vector, i_am_a_developer=i_am_a_developer
        )

    async def get_personal_recommendation(
        self,
        user_id: int,
    ) -> RecommendationResponse:
        """
        Get personalized recommendations based on user's query history.

        Args:
            user_id: The ID of the user to get recommendations for

        Returns:
            RecommendationResponse containing personalized recommendations with explanations
        """
        # Get user's query history
        user_history = await self.ai_support_repository.get_user_query_history(user_id)

        # Get recommendations from AI
        recommendations_text = await self.ai_generation_repository.get_recommendations(
            user_history=user_history, max_recommendations=5
        )

        # Parse recommendations into structured format
        recommendations = []
        for line in recommendations_text.strip().split("\n"):
            if line.startswith("- "):
                # Extract topic and explanation
                parts = line[2:].split(": ", 1)
                if len(parts) == 2:
                    topic, explanation = parts
                    recommendations.append(
                        Recommendation(topic=topic, explanation=explanation)
                    )

        return RecommendationResponse(recommendations=recommendations)
