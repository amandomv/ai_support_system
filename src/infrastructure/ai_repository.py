import logging

from openai import OpenAI

from src.application.interfaces.ai_interface import AIInterface
from src.config.settings import get_settings
from src.types.embeddings import Embedding, EmbeddingResponse


class AIRepository(AIInterface):
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"Loading OpenAI API key: {settings.OPENAI_API_KEY[:8]}..."
        )  # Only log first 8 chars for security
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def generate_embeddings(self, text: str) -> EmbeddingResponse:
        try:
            response = self.client.embeddings.create(
                model=self.model, input=text, encoding_format="float"
            )
            embedding_data = response.data[0]

            return EmbeddingResponse(
                embedding=Embedding(vector=embedding_data.embedding),
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            )
        except Exception as e:
            # Log the error and re-raise
            self.logger.error(f"Error generating embedding: {str(e)}")
            raise


async def get_ai_repository() -> AIInterface:
    """
    Get an instance of the AIRepository.

    Returns:
        AIInterface: An instance of the repository for AI operations.
    """
    return AIRepository()
