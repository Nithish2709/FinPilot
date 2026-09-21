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


@router.get(
    "/health/llm",
    status_code=status.HTTP_200_OK,
    summary="LLM Provider Health Check",
    description="Verifies Ollama server connectivity and configured model presence.",
)
async def get_llm_health():
    """Checks local Ollama server and configured model status."""
    from app.agent.ollama_provider import OllamaProvider
    provider = OllamaProvider()
    return await provider.check_health()
