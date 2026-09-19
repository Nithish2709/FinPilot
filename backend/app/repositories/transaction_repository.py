from datetime import date
from decimal import Decimal
from typing import Optional, Sequence, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    """Handles database persistence and queries for transactions, strictly scoped to authenticated user."""

    @staticmethod
    async def create_batch(db: AsyncSession, transactions: list[Transaction]) -> list[Transaction]:
        """Inserts transactions in batch, avoiding individual row transactions."""
        db.add_all(transactions)
        await db.commit()
        return transactions

    @staticmethod
    async def get_by_user_filtered(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        account_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Sequence[Transaction], int]:
        """
        Retrieves paginated transactions with optional filters.
        Always strictly filtered by user_id.
        """
        base_query = select(Transaction).where(Transaction.user_id == user_id)

        if start_date:
            base_query = base_query.where(Transaction.transaction_date >= start_date)
        if end_date:
            base_query = base_query.where(Transaction.transaction_date <= end_date)
        if category:
            base_query = base_query.where(Transaction.category.ilike(f"%{category}%"))
        if transaction_type:
            base_query = base_query.where(Transaction.transaction_type == transaction_type.upper())
        if account_id:
            base_query = base_query.where(Transaction.account_id == account_id)

        # Count total matching
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = (await db.execute(count_query)).scalar() or 0

        # Fetch page ordered by date descending
        paged_query = (
            base_query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await db.execute(paged_query)).scalars().all()

        return items, total_count

    @staticmethod
    async def get_existing_transactions_for_fingerprinting(
        db: AsyncSession,
        user_id: uuid.UUID,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> Sequence[Transaction]:
        """Fetches transactions in the date range to check for duplicate fingerprints."""
        query = select(Transaction).where(Transaction.user_id == user_id)
        if min_date:
            query = query.where(Transaction.transaction_date >= min_date)
        if max_date:
            query = query.where(Transaction.transaction_date <= max_date)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_all_valid_by_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Sequence[Transaction]:
        """Fetches valid, non-duplicate transactions for user within date boundaries."""
        query = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_valid == True,
            Transaction.is_duplicate == False,
        )
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        query = query.order_by(Transaction.transaction_date.asc())
        result = await db.execute(query)
        return result.scalars().all()
