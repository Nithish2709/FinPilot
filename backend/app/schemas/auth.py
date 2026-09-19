import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address", json_schema_extra={"example": "user@example.com"})
    password: str = Field(..., min_length=8, description="User password", json_schema_extra={"example": "StrongPassword123!"})
    name: str = Field(..., min_length=1, description="User full name", json_schema_extra={"example": "Test User"})


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address", json_schema_extra={"example": "user@example.com"})
    password: str = Field(..., description="User password", json_schema_extra={"example": "StrongPassword123!"})


class UserResponse(BaseModel):
    """Schema for public user profile response."""

    id: uuid.UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Valid refresh token")


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str
