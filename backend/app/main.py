from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status

from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.core.database import create_mongo_client

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    client = create_mongo_client()
    application.state.mongo_client = client
    try:
        yield
    finally:
        if client is not None:
            await client.close()


app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Multi-agent AI management platform.",
    lifespan=lifespan,
)
app.include_router(users_router, prefix=settings.api_prefix)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    """Liveness probe: confirms that the API process is running."""
    return {
        "status": "ok",
        "service": "vn101-ai-office-api",
        "environment": settings.app_env,
    }


@app.get("/readyz", tags=["system"])
async def readyz(request: Request) -> dict[str, str]:
    """Readiness probe: confirms that required infrastructure is reachable."""
    client = getattr(request.app.state, "mongo_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB is not configured",
        )
    try:
        await client.admin.command("ping")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB is unavailable",
        ) from None
    return {"status": "ready", "database": "connected"}


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }
