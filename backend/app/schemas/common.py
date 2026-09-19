from typing import Any
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Service status indicator", json_schema_extra={"example": "ok"})
    service: str = Field(..., description="Name of the service", json_schema_extra={"example": "finpilot-backend"})



class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    status: str = Field(default="error", description="Error status indicator")
    message: str = Field(..., description="Human-readable error description")
    details: Any | None = Field(default=None, description="Optional detailed error context")
