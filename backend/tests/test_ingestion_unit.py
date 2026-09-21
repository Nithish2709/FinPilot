import pytest
from datetime import date
from decimal import Decimal

from app.models.transaction import TransactionType
from app.services.ingestion.models import RawRecord, NormalizedTransaction
from app.services.ingestion.normalizer import Normalizer
from app.services.ingestion.validators import TransactionValidator
from app.services.ingestion.duplicate_detector import DuplicateDetector
import uuid


def test_normalizer_date_parsing():
    assert Normalizer.parse_date("2026-09-15") == date(2026, 9, 15)
    assert Normalizer.parse_date("15-09-2026") == date(2026, 9, 15)
    assert Normalizer.parse_date("15/09/2026") == date(2026, 9, 15)
    assert Normalizer.parse_date("15 Sep 2026") == date(2026, 9, 15)
    assert Normalizer.parse_date("invalid-date") is None


def test_normalizer_amount_parsing():
    assert Normalizer.parse_amount("₹1,25,000.50") == Decimal("125000.50")
    assert Normalizer.parse_amount("$1,200.00") == Decimal("1200.00")
    assert Normalizer.parse_amount("(500.00)") == Decimal("-500.00")
    assert Normalizer.parse_amount("-250.75") == Decimal("-250.75")
    assert Normalizer.parse_amount("not-a-number") is None


def test_normalizer_record_debit_credit():
    # Record with Debit column
    rec1 = RawRecord(
        row_number=2,
        raw_data={"Date": "2026-09-01", "Description": "Swiggy Food", "Debit": "450.00", "Credit": ""},
    )
    norm1 = Normalizer.normalize_record(rec1)
    assert norm1.transaction_date == date(2026, 9, 1)
    assert norm1.amount == Decimal("450.00")
    assert norm1.transaction_type == TransactionType.DEBIT.value

    # Record with Credit column
    rec2 = RawRecord(
        row_number=3,
        raw_data={"Date": "2026-09-02", "Narration": "Salary Credit", "Debit": "", "Credit": "75000.00"},
    )
    norm2 = Normalizer.normalize_record(rec2)
    assert norm2.amount == Decimal("75000.00")
    assert norm2.transaction_type == TransactionType.CREDIT.value

    # Record with Refund
    rec3 = RawRecord(
        row_number=4,
        raw_data={"Txn Date": "2026-09-03", "Details": "Amazon Refund Shoes", "Deposit": "1999.00"},
    )
    norm3 = Normalizer.normalize_record(rec3)
    assert norm3.amount == Decimal("1999.00")
    assert norm3.transaction_type == TransactionType.REFUND.value


def test_transaction_validator():
    # Valid transaction
    valid_txn = NormalizedTransaction(
        row_number=1,
        transaction_date=date(2026, 9, 1),
        description="Grocery Store",
        amount=Decimal("150.00"),
        transaction_type="DEBIT",
    )
    validated = TransactionValidator.validate(valid_txn)
    assert validated.is_valid is True
    assert validated.validation_error is None

    # Invalid: missing date
    invalid_date = NormalizedTransaction(
        row_number=2,
        transaction_date=None,
        description="Grocery Store",
        amount=Decimal("150.00"),
        transaction_type="DEBIT",
    )
    validated = TransactionValidator.validate(invalid_date)
    assert validated.is_valid is False
    assert "date" in validated.validation_error.lower()

    # Invalid: missing description
    invalid_desc = NormalizedTransaction(
        row_number=3,
        transaction_date=date(2026, 9, 1),
        description="",
        amount=Decimal("150.00"),
        transaction_type="DEBIT",
    )
    validated = TransactionValidator.validate(invalid_desc)
    assert validated.is_valid is False
    assert "description" in validated.validation_error.lower()

    # Invalid: non-positive amount
    invalid_amt = NormalizedTransaction(
        row_number=4,
        transaction_date=date(2026, 9, 1),
        description="Coffee",
        amount=Decimal("0.00"),
        transaction_type="DEBIT",
    )
    validated = TransactionValidator.validate(invalid_amt)
    assert validated.is_valid is False
    assert "amount" in validated.validation_error.lower()


def test_duplicate_detector():
    user_id = uuid.uuid4()
    acc_id = uuid.uuid4()

    txn1 = NormalizedTransaction(
        row_number=1,
        transaction_date=date(2026, 9, 1),
        description="Netflix",
        amount=Decimal("649.00"),
        merchant="Netflix",
        transaction_type="DEBIT",
    )
    txn2 = NormalizedTransaction(
        row_number=2,
        transaction_date=date(2026, 9, 1),
        description="Netflix",
        amount=Decimal("649.00"),
        merchant="Netflix",
        transaction_type="DEBIT",
    )
    # Different date is NOT duplicate
    txn3 = NormalizedTransaction(
        row_number=3,
        transaction_date=date(2026, 10, 1),
        description="Netflix",
        amount=Decimal("649.00"),
        merchant="Netflix",
        transaction_type="DEBIT",
    )

    batch = [txn1, txn2, txn3]
    processed = DuplicateDetector.filter_batch_duplicates(user_id, batch, set(), acc_id)

    assert processed[0].is_duplicate is False
    assert processed[1].is_duplicate is True
    assert processed[2].is_duplicate is False
