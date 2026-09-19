from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class RawRecord:
    """Raw extracted row/entry from a statement before normalization."""
    row_number: int
    raw_data: Dict[str, Any]


@dataclass
class NormalizedTransaction:
    """Standardized transaction representation across all input formats."""
    row_number: int
    transaction_date: Optional[date]
    description: str
    amount: Optional[Decimal]
    currency: str = "INR"
    transaction_type: str = "UNKNOWN"
    merchant: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    external_reference: Optional[str] = None
    is_valid: bool = True
    validation_error: Optional[str] = None
    is_duplicate: bool = False
