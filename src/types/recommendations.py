from pydantic import BaseModel


class Recommendation(BaseModel):
    """Model for a single recommendation."""

    topic: str
    explanation: str


class RecommendationResponse(BaseModel):
    """Response model containing a list of recommendations."""

    recommendations: list[Recommendation]
