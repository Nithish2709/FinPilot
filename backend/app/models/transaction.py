import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.document import Document


class TransactionType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    REFUND = "REFUND"
    TRANSFER = "TRANSFER"
    UNKNOWN = "UNKNOWN"


class Transaction(Base):
    """SQLAlchemy model representing a financial transaction."""

    __tablename__ = "transactions"

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
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    transaction_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )
    merchant: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        default=TransactionType.UNKNOWN.value,
        nullable=False,
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    external_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    is_duplicate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    validation_error: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
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
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    account: Mapped[Optional["Account"]] = relationship("Account", back_populates="transactions")
    source_document: Mapped[Optional["Document"]] = relationship("Document", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
    )
