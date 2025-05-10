from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for user queries."""

    query: str
    user_id: int
