import logging

from openai import OpenAI

from src.application.ai_interface import AIInterface
from src.config.settings import get_settings
from src.types.embeddings import Embedding, EmbeddingResponse


class AIRepository(AIInterface):
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.logger = logging.getLogger(__name__)

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
