from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_payment import RecurringPayment, RecurringStatus


class RecurringRepository:
    """Handles recurring payments persistence and retrieval, strictly user-scoped."""

    @staticmethod
    async def get_all_by_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> Sequence[RecurringPayment]:
        query = select(RecurringPayment).where(RecurringPayment.user_id == user_id)
        if status:
            query = query.where(RecurringPayment.status == status)
        query = query.order_by(RecurringPayment.next_expected_date.asc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def upsert_detected(
        db: AsyncSession,
        user_id: uuid.UUID,
        merchant: str,
        average_amount,
        frequency: str,
        last_payment_date,
        next_expected_date,
        confidence,
        status: str = RecurringStatus.ACTIVE.value,
    ) -> RecurringPayment:
        query = select(RecurringPayment).where(
            RecurringPayment.user_id == user_id,
            RecurringPayment.merchant == merchant,
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            existing.average_amount = average_amount
            existing.frequency = frequency
            existing.last_payment_date = last_payment_date
            existing.next_expected_date = next_expected_date
            existing.confidence = confidence
            existing.status = status
            await db.commit()
            await db.refresh(existing)
            return existing

        new_rec = RecurringPayment(
            user_id=user_id,
            merchant=merchant,
            average_amount=average_amount,
            frequency=frequency,
            last_payment_date=last_payment_date,
            next_expected_date=next_expected_date,
            confidence=confidence,
            status=status,
        )
        db.add(new_rec)
        await db.commit()
        await db.refresh(new_rec)
        return new_rec
