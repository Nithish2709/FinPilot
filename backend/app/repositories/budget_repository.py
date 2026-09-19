from datetime import date
from decimal import Decimal
from typing import Optional, Sequence
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType


class BudgetRepository:
    """Handles budget database operations, strictly scoped to user_id."""

    @staticmethod
    async def create(db: AsyncSession, budget: Budget) -> Budget:
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget

    @staticmethod
    async def get_by_id(db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Budget]:
        query = select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: uuid.UUID, is_active: Optional[bool] = None) -> Sequence[Budget]:
        query = select(Budget).where(Budget.user_id == user_id)
        if is_active is not None:
            query = query.where(Budget.is_active == is_active)
        query = query.order_by(Budget.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, budget: Budget) -> Budget:
        await db.commit()
        await db.refresh(budget)
        return budget

    @staticmethod
    async def delete(db: AsyncSession, budget_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        budget = await BudgetRepository.get_by_id(db, budget_id, user_id)
        if not budget:
            return False
        await db.delete(budget)
        await db.commit()
        return True

    @staticmethod
    async def get_spent_for_category(
        db: AsyncSession,
        user_id: uuid.UUID,
        category: str,
        start_date: date,
        end_date: Optional[date] = None,
    ) -> Decimal:
        """Calculates total spent amount in a category for a given period."""
        query = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.DEBIT.value,
            Transaction.is_valid == True,
            Transaction.is_duplicate == False,
            Transaction.transaction_date >= start_date,
        )
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)

        result = await db.execute(query)
        txns = result.scalars().all()

        spent = Decimal("0.00")
        for t in txns:
            # Match category case-insensitively
            if t.category and t.category.strip().lower() == category.strip().lower():
                spent += t.amount or Decimal("0.00")
        return spent
