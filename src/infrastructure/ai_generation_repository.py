import logging
from functools import cache

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI
from pydantic import BaseModel, Field

from src.application.interfaces.ai_generation_interface import AIGenerationInterface
from src.config.settings import get_settings
from src.types.documents import FaqDocument
from src.types.embeddings import Embedding, EmbeddingResponse


class FormattedResponse(BaseModel):
    """Model for the formatted response."""

    answer: str = Field(description="The main answer to the user's question")
    used_documents: list[str] = Field(
        description="List of document titles used to generate the answer"
    )


class AIGenerationRepository(AIGenerationInterface):
    def __init__(self, client: OpenAI) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = "text-embedding-3-small"
        self.chat_model = "gpt-3.5-turbo"
        self.client = client

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

    async def generate_response(
        self, query: str, context_docs: list[FaqDocument]
    ) -> tuple[str, list[FaqDocument]]:
        try:
            # Prepare the context from the documents
            context = "\n\n".join(
                f"Document: {doc.title}\nContent: {doc.text}" for doc in context_docs
            )

            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are a technical support assistant for the Shakers platform.
                Your task is to answer user questions using ONLY the provided context.
                If the answer is not in the context, say you don't have that information.

                Format your response as follows:
                - Start with a clear, concise answer
                - If relevant, provide additional context or examples
                - Keep the tone professional but friendly
                - Do not mention that you are an AI or that you are using context

                {format_instructions}""",
                    ),
                    (
                        "human",
                        """Context:
                {context}

                User question: {query}""",
                    ),
                ]
            )

            # Initialize the output parser
            output_parser = PydanticOutputParser(pydantic_object=FormattedResponse)

            # Format the prompt with the context and query
            formatted_prompt = prompt.format_messages(
                context=context,
                query=query,
                format_instructions=output_parser.get_format_instructions(),
            )

            # Generate the response using the existing client
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[  # pyright: ignore
                    {"role": "system", "content": formatted_prompt[0].content},
                    {"role": "user", "content": formatted_prompt[1].content},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            # Parse the response
            parsed_response = output_parser.parse(response.choices[0].message.content)  # pyright: ignore

            # Find which documents were used
            used_docs = []
            for doc in context_docs:
                if doc.title in parsed_response.used_documents:
                    used_docs.append(doc)

            return parsed_response.answer, used_docs

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise


@cache
def get_ai_client() -> OpenAI:
    logger = logging.getLogger(__name__)
    settings = get_settings()
    logger.info(
        f"Loading OpenAI API key: {settings.OPENAI_API_KEY[:8]}..."
    )  # Only log first 8 chars for security
    return OpenAI(api_key=settings.OPENAI_API_KEY)


async def get_ai_generation_repository() -> AIGenerationInterface:
    """
    Get an instance of the AIGenerationRepository.

    Returns:
        AIGenerationInterface: An instance of the repository for AI operations.
    """
    client = get_ai_client()
    return AIGenerationRepository(client)
