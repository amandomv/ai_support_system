import uvicorn
from fastapi import FastAPI
from router import router

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
    uvicorn.run(app, host="localhost", port=8001)
