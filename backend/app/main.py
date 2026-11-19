from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multi-agent AI management platform.",
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "vn101-ai-office-api",
        "environment": settings.app_env,
    }


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }
