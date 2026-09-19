from fastapi import APIRouter, status

from app.core.config import settings
from app.schemas.common import HealthCheckResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns the health status and service identifier.",
)
async def get_health() -> HealthCheckResponse:
    """Health check endpoint for service monitoring."""
    return HealthCheckResponse(
        status="ok",
        service=settings.APP_NAME,
    )
