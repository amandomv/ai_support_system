from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FaqCategory(str, Enum):
    """Categories for FAQ documents."""

    PLATFORM_OVERVIEW = "platform_overview"
    PAYMENTS = "payments"
    FREELANCERS = "freelancers"
    CLIENTS = "clients"
    PLATFORM_FEATURES = "platform_features"
    SUPPORT = "support"
    BEST_PRACTICES = "best_practices"


class FaqDocumentBaseData(BaseModel):
    """Base data model for FAQ documents used in responses."""

    title: str
    link: str


class FaqDocument(BaseModel):
    """
    Model for FAQ documents stored in the database.

    This model represents a FAQ document with its content, metadata,
    and embedding information.
    """

    id: int | None = Field(None, description="Unique identifier for the FAQ document")
    title: str = Field(..., description="Title of the FAQ document")
    link: str = Field(..., description="URL or reference link to the original document")
    text: str = Field(..., description="Full text content of the FAQ document")
    category: FaqCategory = Field(..., description="Category of the FAQ document")
    embedding: list[float] = Field(
        [], description="Vector embedding of the document text for semantic search"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Timestamp when the document was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Timestamp when the document was last updated",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True  # For ORM compatibility
