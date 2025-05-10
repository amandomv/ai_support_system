from fastapi import APIRouter, Depends

from src.application.ai_support_manager import AISupportManager, SupportResponse
from src.dependencies.fastapi_depends import get_ai_support_manager_dependency
from src.types.recommendations import RecommendationResponse
from src.types.support import QueryRequest

router = APIRouter(
    prefix="/ai_system",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


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
        request: The query request containing the user's question, ID, and developer status
        ai_support_manager: The AI support manager instance (injected by FastAPI)

    Returns:
        SupportResponse containing the generated response and relevant links
    """
    return await ai_support_manager.generate_ai_support_response(
        query=request.query,
        user_id=request.user_id,
        i_am_a_developer=request.i_am_a_developer,
    )


@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_personal_recommendations(
    user_id: int,
    ai_support_manager: AISupportManager = Depends(get_ai_support_manager_dependency),
) -> RecommendationResponse:
    """
    Get personalized recommendations based on user's query history.

    Args:
        user_id: The ID of the user to get recommendations for
        ai_support_manager: AISupportManager instance for handling the request

    Returns:
        RecommendationResponse containing personalized recommendations with explanations
    """
    return await ai_support_manager.get_personal_recommendation(
        user_id=user_id,
    )
