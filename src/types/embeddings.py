from typing import Any

from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """Type for a single embedding vector."""

    vector: list[float] = Field(
        ...,
        description="Vector of floats representing the embedding",
        min_length=1536,
        max_length=1536,
    )


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""

    embedding: Embedding = Field(..., description="The generated embedding vector")
    model: str = Field(..., description="The model used to generate the embedding")
    usage: dict[str, Any] = Field(
        ..., description="Usage statistics for the embedding generation"
    )


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""

    text: str = Field(
        ..., description="The text to generate an embedding for", min_length=1
    )
    model: str = Field(
        default="text-embedding-3-small",
        description="The model to use for embedding generation",
    )
