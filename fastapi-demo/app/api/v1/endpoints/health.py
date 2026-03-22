"""Health check endpoint."""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> dict:
    """Return application health status."""
    return {"status": "healthy", "version": "1.0.0"}
