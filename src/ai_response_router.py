from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@router.get("/hello")
async def hello_world() -> dict[str, str]:
    """Simple hello world endpoint."""
    return {"message": "Hola Mundo!"}
