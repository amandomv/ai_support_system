from pydantic import BaseModel

from src.types.documents import FaqDocument


class SupportResponse(BaseModel):
    """Response containing the AI support response."""

    response: str
    docs_used: list[FaqDocument]
