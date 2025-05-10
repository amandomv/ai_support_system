from pydantic import BaseModel

from src.types.documents import FaqDocument


class QueryRequest(BaseModel):
    """Request model for AI support queries."""

    query: str
    user_id: int
    i_am_a_developer: bool = False


class SupportResponse(BaseModel):
    """Response containing the AI support response."""

    response: str
    docs_used: list[FaqDocument]
