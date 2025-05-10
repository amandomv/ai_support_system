from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.application.ai_support_manager import AISupportManager, SupportResponse
from src.dependencies.fastapi_depends import get_ai_support_manager_dependency

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


class QueryRequest(BaseModel):
    query: str
    user_id: int


@router.get("/hello")
async def hello_world() -> dict[str, str]:
    """Simple hello world endpoint."""
    return {"message": "Hola Mundo!"}


@router.post("/ai_faq_search", response_model=SupportResponse)
async def get_ai_faq_search(
    request: QueryRequest,
    ai_support_manager: AISupportManager = Depends(get_ai_support_manager_dependency),
) -> SupportResponse:
    """
    Process a user query and return an AI-generated response with relevant links.

    Args:
        request: The query request containing the user's question and ID
        ai_support_manager: The AI support manager instance (injected by FastAPI)

    Returns:
        SupportResponse containing the generated response and relevant links
    """
    return await ai_support_manager.generate_ai_support_response(
        query=request.query, user_id=request.user_id
    )
