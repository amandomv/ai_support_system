import uvicorn
from fastapi import FastAPI

from src.ai_response_router import router
from src.config.settings import get_settings

app = FastAPI(
    title="AI Support System API",
    description="API for AI Support System with Swagger UI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include the router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=get_settings().APP_PORT)
