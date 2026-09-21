from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:
    """Handles database persistence and retrieval for accounts, strictly user-scoped."""

    @staticmethod
    async def get_by_id(db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Account]:
        query = select(Account).where(Account.id == account_id, Account.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Account]:
        query = select(Account).where(Account.user_id == user_id).order_by(Account.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, account: Account) -> Account:
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def get_or_create_default(db: AsyncSession, user_id: uuid.UUID, name: str = "Default Account") -> Account:
        query = select(Account).where(Account.user_id == user_id, Account.name == name)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        new_account = Account(
            user_id=user_id,
            name=name,
            account_type="Savings",
            currency="INR",
            is_active=True,
        )
        db.add(new_account)
        await db.commit()
        await db.refresh(new_account)
        return new_account
