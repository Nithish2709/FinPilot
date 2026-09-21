import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple

from app.models.transaction import TransactionType
from app.services.ingestion.models import NormalizedTransaction, RawRecord


class Normalizer:
    """
    Normalizes raw statement records into standard NormalizedTransaction objects.
    Maps varying column headers, parses dates, sanitizes currency/amounts,
    and classifies transaction types (DEBIT, CREDIT, REFUND, TRANSFER).
    """

    # Common column alias sets (case-insensitive)
    DATE_ALIASES = {
        "date", "txn date", "transaction date", "trans date", "value date",
        "booking date", "post date", "posted date"
    }
    DESC_ALIASES = {
        "description", "narration", "details", "particulars", "transaction details",
        "memo", "remarks", "reference / description"
    }
    MERCHANT_ALIASES = {
        "merchant", "payee", "beneficiary", "vendor", "party"
    }
    AMOUNT_ALIASES = {
        "amount", "txn amount", "transaction amount", "net amount", "total"
    }
    DEBIT_ALIASES = {
        "debit", "withdrawal", "withdrawals", "dr", "debit amount", "paid out"
    }
    CREDIT_ALIASES = {
        "credit", "deposit", "deposits", "cr", "credit amount", "paid in"
    }
    TYPE_ALIASES = {
        "type", "transaction type", "txn type", "cr/dr", "d/c"
    }
    REF_ALIASES = {
        "reference", "reference no", "ref no", "external reference", "ref",
        "cheque no", "chq no", "utr", "transaction id", "txn id"
    }

    # Supported date formats
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%d/%m/%y",
        "%d-%m-%y",
    ]

    @classmethod
    def _find_field_value(cls, raw_dict: Dict[str, Any], aliases: set[str]) -> Optional[str]:
        for k, v in raw_dict.items():
            if k.strip().lower() in aliases and v is not None and str(v).strip() != "":
                return str(v).strip()
        return None

    @classmethod
    def parse_date(cls, val_str: str) -> Optional[date]:
        """Parses date string against known date patterns."""
        cleaned = val_str.strip()
        # Remove time component if present
        cleaned = re.sub(r"\s+\d{1,2}:\d{2}(:\d{2})?.*$", "", cleaned)

        for fmt in cls.DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).date()
            except ValueError:
                continue
        return None

    @classmethod
    def clean_amount_str(cls, val_str: str) -> str:
        """Removes currency symbols (₹, $, €, £), commas, and spaces."""
        cleaned = re.sub(r"[₹\$€£,\s]", "", val_str)
        return cleaned

    @classmethod
    def parse_amount(cls, val_str: str) -> Optional[Decimal]:
        """Parses string into Decimal preserving precision."""
        cleaned = cls.clean_amount_str(val_str)
        # Handle trailing CR/DR, or enclosing parentheses e.g. (100.00)
        is_negative = False
        if cleaned.startswith("(") and cleaned.endswith(")"):
            is_negative = True
            cleaned = cleaned[1:-1]
        elif cleaned.endswith("-") or cleaned.startswith("-"):
            is_negative = True
            cleaned = cleaned.replace("-", "")

        try:
            val = Decimal(cleaned)
            return -val if is_negative else val
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def determine_type_and_amount(
        cls,
        raw_dict: Dict[str, Any],
        desc: str,
    ) -> Tuple[Optional[Decimal], str]:
        """
        Determines the final positive transaction amount and transaction type
        (DEBIT, CREDIT, REFUND, TRANSFER, UNKNOWN) from debit/credit columns or amount column.
        """
        desc_upper = desc.upper()

        debit_val_str = cls._find_field_value(raw_dict, cls.DEBIT_ALIASES)
        credit_val_str = cls._find_field_value(raw_dict, cls.CREDIT_ALIASES)
        amount_val_str = cls._find_field_value(raw_dict, cls.AMOUNT_ALIASES)
        type_hint = cls._find_field_value(raw_dict, cls.TYPE_ALIASES)

        # 1. Separate Debit & Credit columns
        if debit_val_str or credit_val_str:
            debit_amt = cls.parse_amount(debit_val_str) if debit_val_str else None
            credit_amt = cls.parse_amount(credit_val_str) if credit_val_str else None

            if debit_amt is not None and debit_amt != Decimal(0):
                final_amt = abs(debit_amt)
                # Check for refund/transfer indications in description
                if "REFUND" in desc_upper or "REVERSAL" in desc_upper:
                    return final_amt, TransactionType.REFUND.value
                if "TRANSFER" in desc_upper or "NEFT" in desc_upper or "IMPS" in desc_upper:
                    return final_amt, TransactionType.TRANSFER.value
                return final_amt, TransactionType.DEBIT.value

            if credit_amt is not None and credit_amt != Decimal(0):
                final_amt = abs(credit_amt)
                if "REFUND" in desc_upper or "REVERSAL" in desc_upper:
                    return final_amt, TransactionType.REFUND.value
                if "TRANSFER" in desc_upper:
                    return final_amt, TransactionType.TRANSFER.value
                return final_amt, TransactionType.CREDIT.value

        # 2. Single Amount column
        if amount_val_str:
            parsed = cls.parse_amount(amount_val_str)
            if parsed is None:
                return None, TransactionType.UNKNOWN.value

            final_amt = abs(parsed)
            # Check type hint first
            if type_hint:
                th_upper = type_hint.strip().upper()
                if "REFUND" in th_upper or "REVERSAL" in desc_upper or "REFUND" in desc_upper:
                    return final_amt, TransactionType.REFUND.value
                if th_upper in {"CR", "CREDIT", "DEPOSIT"}:
                    return final_amt, TransactionType.CREDIT.value
                if th_upper in {"DR", "DEBIT", "WITHDRAWAL"}:
                    return final_amt, TransactionType.DEBIT.value
                if "TRANSFER" in th_upper:
                    return final_amt, TransactionType.TRANSFER.value

            # Check description keywords
            if "REFUND" in desc_upper or "REVERSAL" in desc_upper:
                return final_amt, TransactionType.REFUND.value
            if "TRANSFER" in desc_upper:
                return final_amt, TransactionType.TRANSFER.value

            # Check signed amount
            if parsed < Decimal(0):
                return final_amt, TransactionType.DEBIT.value
            elif parsed > Decimal(0):
                # Positive in single column: usually CREDIT or DEBIT depending on convention, default to DEBIT for purchases
                if "SALARY" in desc_upper or "CREDIT" in desc_upper or "DEPOSIT" in desc_upper:
                    return final_amt, TransactionType.CREDIT.value
                return final_amt, TransactionType.DEBIT.value

        return None, TransactionType.UNKNOWN.value

    @classmethod
    def normalize_record(cls, record: RawRecord) -> NormalizedTransaction:
        raw = record.raw_data

        # Description
        desc = cls._find_field_value(raw, cls.DESC_ALIASES) or ""
        # If no explicit description, fallback to merchant or join fields
        if not desc:
            merchant_fallback = cls._find_field_value(raw, cls.MERCHANT_ALIASES)
            if merchant_fallback:
                desc = merchant_fallback

        # Date
        date_str = cls._find_field_value(raw, cls.DATE_ALIASES)
        parsed_date = cls.parse_date(date_str) if date_str else None

        # Merchant
        merchant = cls._find_field_value(raw, cls.MERCHANT_ALIASES)
        if not merchant and desc:
            # Extract possible merchant (e.g. from "UPI/Swiggy/..." or "POS PURCHASE XYZ")
            merchant = desc.split("/")[0].strip() if "/" in desc else None

        # Amount & Transaction Type
        amount, txn_type = cls.determine_type_and_amount(raw, desc)

        # External reference
        ext_ref = cls._find_field_value(raw, cls.REF_ALIASES)

        return NormalizedTransaction(
            row_number=record.row_number,
            transaction_date=parsed_date,
            description=desc.strip(),
            amount=amount,
            currency="INR",
            transaction_type=txn_type,
            merchant=merchant.strip() if merchant else None,
            category=None,
            subcategory=None,
            external_reference=ext_ref.strip() if ext_ref else None,
            is_valid=True,
            validation_error=None,
        )
