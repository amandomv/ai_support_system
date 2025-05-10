import logging
from functools import cache

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI
from pydantic import BaseModel, Field

from src.application.interfaces.ai_generation_interface import AIGenerationInterface
from src.application.interfaces.ai_support_interface import UserQueryHistory
from src.config.settings import get_settings
from src.types.documents import FaqDocument
from src.types.embeddings import Embedding, EmbeddingResponse


class FormattedResponse(BaseModel):
    """Model for the formatted response."""

    answer: str = Field(
        description="The main answer to the user's question. Should be detailed and well-structured, including examples, explanations, and best practices."
    )
    used_documents: list[str] = Field(
        description="List of document titles used to generate the answer"
    )


class AIGenerationRepository(AIGenerationInterface):
    def __init__(self, client: OpenAI) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = "text-embedding-3-small"
        self.chat_model = "gpt-4"
        self.client = client

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
        try:
            # Create a prompt for summarization
            prompt = f"""Please provide a concise summary of the following text, focusing on the key points and main ideas. 
            The summary should be clear and informative while being significantly shorter than the original text.

            Text to summarize:
            {text}

            Summary:"""

            # Generate the summary using GPT-4
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates extensive and informative summaries, it needs to capture all the infomation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused summaries
                max_tokens=150,   # Limit summary length
            )

            summary = response.choices[0].message.content.strip()
            self.logger.debug(f"Generated summary of length {len(summary)} characters")
            return summary

        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            raise

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

    @staticmethod
    def _create_prompt_template() -> ChatPromptTemplate:
        """Create the prompt template for the chat."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a support assistant for the Shakers platform.
                Your task is to answer user questions using ONLY the provided context.
                If the answer is not in the context, say you don't have that information.

                Provide detailed responses that:
                1. Start with a clear, direct answer
                2. Include specific examples and use cases
                3. Explain technical terms and concepts
                4. Add relevant tips and best practices
                5. Use bullet points for lists and steps
                6. Use code blocks for technical content

                Keep the tone professional but friendly. Do not mention you are an AI.
                Be thorough and detailed in your explanations.

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

    @staticmethod
    def _prepare_context(context_docs: list[FaqDocument]) -> str:
        """Prepare the context string from the documents."""
        return "\n\n".join(
            f"Document: {doc.title}\nContent: {doc.llm_summary}" for doc in context_docs
        )

    @staticmethod
    def _get_used_documents(
        parsed_response: FormattedResponse, context_docs: list[FaqDocument]
    ) -> list[FaqDocument]:
        """Get the documents that were used in the response."""
        return [
            doc for doc in context_docs if doc.title in parsed_response.used_documents
        ]

    async def generate_response(
        self, query: str, context_docs: list[FaqDocument]
    ) -> tuple[str, list[FaqDocument]]:
        try:
            # Prepare the context from the documents
            context = self._prepare_context(context_docs)

            # Create the prompt template
            prompt = self._create_prompt_template()

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
                temperature=0.8,
                max_tokens=2000,
            )

            # Parse the response
            parsed_response = output_parser.parse(response.choices[0].message.content)  # pyright: ignore

            # Find which documents were used
            used_docs = self._get_used_documents(parsed_response, context_docs)

            return parsed_response.answer, used_docs

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise

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
                - [topic]: [explanation]
                - [topic]: [explanation]
                ...

        Raises:
            Exception: If there's an error generating recommendations
        """
        try:
            # Create a prompt that focuses on user's interests based on history
            history_text = "\n".join(
                [
                    f"- Question: {history.user_question}\n  Response: {history.response}"
                    for history in user_history
                ]
            )
            prompt = f"""Based on the user's previous interactions:
{history_text}

Generate {max_recommendations} personalized topic recommendations they might find interesting.
For each recommendation, provide a topic and a brief explanation of why it might be relevant.

Format each recommendation as:
- [topic]: [explanation]

Focus on patterns in their interests and suggest related topics they haven't explored yet."""

            # Get recommendations from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates personalized topic recommendations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
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
