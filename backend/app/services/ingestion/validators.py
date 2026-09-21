from decimal import Decimal
from app.models.transaction import TransactionType
from app.services.ingestion.models import NormalizedTransaction


class TransactionValidator:
    """
    Validates normalized transactions.
    Ensures non-crashing validation by tagging invalid rows with is_valid=False and reason.
    """

    ALLOWED_TRANSACTION_TYPES = {
        TransactionType.DEBIT.value,
        TransactionType.CREDIT.value,
        TransactionType.REFUND.value,
        TransactionType.TRANSFER.value,
        TransactionType.UNKNOWN.value,
    }

    @classmethod
    def validate(cls, txn: NormalizedTransaction) -> NormalizedTransaction:
        errors = []

        # 1. Date presence
        if txn.transaction_date is None:
            errors.append("Missing or unparseable transaction date")

        # 2. Description presence
        if not txn.description or not txn.description.strip():
            errors.append("Missing transaction description")

        # 3. Amount validity
        if txn.amount is None:
            errors.append("Missing or invalid numeric amount")
        elif txn.amount <= Decimal("0"):
            errors.append(f"Transaction amount must be strictly greater than 0, got {txn.amount}")

        # 4. Transaction type
        if txn.transaction_type not in cls.ALLOWED_TRANSACTION_TYPES:
            errors.append(f"Unsupported transaction type: {txn.transaction_type}")

        if errors:
            txn.is_valid = False
            txn.validation_error = "; ".join(errors)
        else:
            txn.is_valid = True
            txn.validation_error = None

        return txn
