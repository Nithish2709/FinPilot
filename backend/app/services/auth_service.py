from datetime import datetime, timezone
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserRegister


class AuthService:
    """Service encapsulating authentication logic."""

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
        """Registers a new user after verifying email uniqueness."""
        normalized_email = user_data.email.strip().lower()
        existing_user = await UserRepository.get_by_email(db, normalized_email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        hashed_pw = hash_password(user_data.password)
        new_user = await UserRepository.create(
            db,
            email=normalized_email,
            password_hash=hashed_pw,
            name=user_data.name,
        )
        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> User:
        """Authenticates user credentials."""
        user = await UserRepository.get_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return user

    @staticmethod
    async def login(db: AsyncSession, login_data: LoginRequest) -> TokenResponse:
        """Logs in user and issues access/refresh tokens."""
        user = await AuthService.authenticate_user(db, login_data)

        access_token = create_access_token(subject=user.id)
        raw_refresh_token, expires_at = create_refresh_token(subject=user.id)

        token_hash = hash_token(raw_refresh_token)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(db_refresh_token)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        """Validates refresh token and issues a new token pair."""
        payload = decode_token(refresh_token_str)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_hash = hash_token(refresh_token_str)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        )
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        expires_at = token_record.expires_at if token_record else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if not token_record or token_record.revoked or (expires_at and expires_at <= now):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )


        user = await UserRepository.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account unavailable or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Revoke previous refresh token
        token_record.revoked = True
        db.add(token_record)

        # Issue new token pair
        new_access_token = create_access_token(subject=user.id)
        new_raw_refresh_token, new_expires_at = create_refresh_token(subject=user.id)

        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_raw_refresh_token),
            expires_at=new_expires_at,
            revoked=False,
        )
        db.add(new_token_record)
        await db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def logout(db: AsyncSession, refresh_token_str: str) -> None:
        """Revokes a refresh token during logout."""
        try:
            payload = decode_token(refresh_token_str)
        except HTTPException:
            # Even if token signature is expired/invalid, attempt to revoke matching hash
            payload = {}

        token_hash = hash_token(refresh_token_str)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.execute(stmt)
        token_records = result.scalars().all()

        if token_records:
            for record in token_records:
                record.revoked = True
                db.add(record)
            await db.commit()

