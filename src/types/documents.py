from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FaqCategory(str, Enum):
    """Categories for FAQ documents."""

    GENERAL = "general"
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
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

    id: Optional[int] = None
    title: str = Field(..., description="Title of the FAQ document")
    link: str = Field(..., description="URL or reference link to the original document")
    text: str = Field(..., description="Full text content of the FAQ document")
    llm_summary: Optional[str] = Field(None, description="AI-generated summary of the document content")
    category: FaqCategory = Field(..., description="Category of the FAQ document")
    embedding: Optional[List[float]] = None
    created_at: Optional[str] = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Timestamp when the document was last updated",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True  # For ORM compatibility
