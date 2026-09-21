from decimal import Decimal
from typing import List, Optional, Sequence
from collections import defaultdict

from app.models.transaction import Transaction, TransactionType
from app.schemas.financial import CategoryBreakdownResponse, CategorySummaryItem


# Deterministic rule-based keyword mapping for category assignment
KEYWORD_CATEGORY_RULES = [
    # (Keywords, Category Name)
    (["swiggy", "zomato", "restaurant", "food", "cafe", "starbucks", "mcdonalds", "burger", "pizza", "dining", "eats"], "Food"),
    (["uber", "ola", "metro", "fuel", "petrol", "diesel", "transport", "irctc", "flight", "indigo", "air india", "taxi", "bus", "toll", "fastag"], "Transport"),
    (["netflix", "spotify", "prime video", "disney", "hotstar", "youtube", "cinema", "movie", "entertainment", "subscription"], "Entertainment"),
    (["electricity", "water bill", "internet", "wifi", "broadband", "bescom", "utility", "recharge", "airtel", "jio", "gas bill"], "Utilities"),
    (["amazon", "flipkart", "myntra", "shopping", "retail", "zara", "clothing", "supermarket", "grocery", "blinkit", "zepto", "instamart"], "Shopping"),
    (["salary", "payroll", "dividend", "interest", "stipend"], "Income"),
    (["hospital", "pharmacy", "medicine", "doctor", "apollo", "medplus", "health", "clinic"], "Healthcare"),
]


class CategoryEngine:
    """
    Deterministic category breakdown aggregator and rule-based classifier.
    Works without LLMs.
    """

    @staticmethod
    def classify_keyword(description: str, merchant: Optional[str] = None) -> str:
        """Determines category from merchant or description keywords if missing."""
        text = f"{merchant or ''} {description or ''}".lower()
        for keywords, cat in KEYWORD_CATEGORY_RULES:
            if any(kw in text for kw in keywords):
                return cat
        return "Uncategorized"

    @classmethod
    def calculate_category_breakdown(
        cls,
        transactions: Sequence[Transaction],
    ) -> CategoryBreakdownResponse:
        category_totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        category_counts: dict[str, int] = defaultdict(int)
        total_expenses = Decimal("0.00")

        for txn in transactions:
            # Only summarize valid non-duplicate expense transactions (DEBIT)
            if not txn.is_valid or txn.is_duplicate:
                continue
            if txn.transaction_type != TransactionType.DEBIT.value:
                continue

            amt = txn.amount or Decimal("0.00")
            # Preserve existing category if already present; otherwise classify deterministically
            category = txn.category
            if not category or not category.strip():
                category = cls.classify_keyword(txn.description, txn.merchant)

            category_totals[category] += amt
            category_counts[category] += 1
            total_expenses += amt

        items: List[CategorySummaryItem] = []
        for cat, cat_amt in category_totals.items():
            if total_expenses > Decimal("0.00"):
                pct = ((cat_amt / total_expenses) * Decimal("100.0")).quantize(Decimal("0.01"))
            else:
                pct = Decimal("0.00")

            items.append(
                CategorySummaryItem(
                    category=cat,
                    amount=cat_amt.quantize(Decimal("0.01")),
                    percentage=pct,
                    transaction_count=category_counts[cat],
                )
            )

        # Sort descending by expense amount
        items.sort(key=lambda x: x.amount, reverse=True)

        return CategoryBreakdownResponse(
            total_expenses=total_expenses.quantize(Decimal("0.01")),
            categories=items,
        )
