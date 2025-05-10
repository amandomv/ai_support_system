from fastapi import FastAPI

from src.ai_response_router import router as ai_router
from src.config.settings import get_settings
from src.infrastructure.prometheus_metrics import setup_prometheus_metrics

app = FastAPI(
    title="AI Support System API",
    description="API for AI Support System with Swagger UI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup Prometheus metrics
setup_prometheus_metrics(app)

# Include routers
app.include_router(ai_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    port = get_settings().APP_PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
