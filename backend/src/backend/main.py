from fastapi import FastAPI
from backend.core.config import settings


app = FastAPI(
    title="Agentic Banking Platform API",
    version=settings.app_version,
    description="Backend for a production-style agentic AI banking platform",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        }