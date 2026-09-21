import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class RecurringFrequency(str, enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    UNKNOWN = "UNKNOWN"


class RecurringStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"


class RecurringPayment(Base):
    """SQLAlchemy model representing detected recurring payments/subscriptions."""

    __tablename__ = "recurring_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    merchant: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    average_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    frequency: Mapped[str] = mapped_column(
        String(50),
        default=RecurringFrequency.MONTHLY.value,
        nullable=False,
    )
    last_payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    next_expected_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.80"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=RecurringStatus.ACTIVE.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recurring_payments")
