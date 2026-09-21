import hashlib
from typing import Optional, Set
import uuid

from app.services.ingestion.models import NormalizedTransaction


class DuplicateDetector:
    """
    Deterministic duplicate detector.
    Computes a cryptographic hash fingerprint over the combination of:
    user_id + transaction_date + amount + merchant + description + account_id + external_reference.
    Maintains legitimate repeated recurring transactions (does not duplicate purely on amount).
    """

    @classmethod
    def compute_fingerprint(
        cls,
        user_id: uuid.UUID,
        txn: NormalizedTransaction,
        account_id: Optional[uuid.UUID] = None,
    ) -> str:
        # Build normalized representation
        date_str = txn.transaction_date.isoformat() if txn.transaction_date else "none"
        amt_str = str(txn.amount) if txn.amount is not None else "0.00"
        desc_str = txn.description.strip().lower()
        merchant_str = (txn.merchant or "").strip().lower()
        account_str = str(account_id) if account_id else "none"
        ext_ref_str = (txn.external_reference or "").strip().lower()

        raw_key = f"{user_id}|{date_str}|{amt_str}|{desc_str}|{merchant_str}|{account_str}|{ext_ref_str}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def filter_batch_duplicates(
        cls,
        user_id: uuid.UUID,
        transactions: list[NormalizedTransaction],
        existing_fingerprints: Set[str],
        account_id: Optional[uuid.UUID] = None,
    ) -> list[NormalizedTransaction]:
        """
        Marks transactions as duplicates if their deterministic fingerprint
        matches an existing database transaction or a preceding item in the same batch.
        """
        seen_fingerprints: Set[str] = set(existing_fingerprints)

        for txn in transactions:
            # Only check duplicates for otherwise valid transactions
            if not txn.is_valid:
                continue

            fp = cls.compute_fingerprint(user_id, txn, account_id)
            if fp in seen_fingerprints:
                txn.is_duplicate = True
            else:
                seen_fingerprints.add(fp)
                txn.is_duplicate = False

        return transactions
