from typing import Any, Dict, List, Literal, Optional, Union
import uuid
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Structured Model Output Schemas
# -------------------------------------------------------------

class AgentToolCall(BaseModel):
    """Structured tool request from model."""
    action: Literal["tool"] = "tool"
    tool: str = Field(..., min_length=1, description="Registered tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool execution arguments")


class AgentFinalResponse(BaseModel):
    """Final natural-language explanation from model."""
    action: Literal["final"] = "final"
    answer: str = Field(..., min_length=1, description="Natural language response explaining findings")


AgentAction = Union[AgentToolCall, AgentFinalResponse]


# -------------------------------------------------------------
# Tool Arguments Validation Schemas
# -------------------------------------------------------------

class MonthlySummaryArgs(BaseModel):
    month: Optional[str] = Field(None, description="Month in YYYY-MM format (e.g. 2026-08)")


class TransactionsArgs(BaseModel):
    category: Optional[str] = Field(None, description="Category filter (e.g. Food, Utilities)")
    transaction_type: Optional[str] = Field(None, description="DEBIT, CREDIT, REFUND, or TRANSFER")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Max transactions to return")


class CategorySpendingArgs(BaseModel):
    month: Optional[str] = Field(None, description="Month in YYYY-MM format")


class RecurringPaymentsArgs(BaseModel):
    pass


class UpcomingObligationsArgs(BaseModel):
    days_ahead: Optional[int] = Field(30, ge=1, le=90, description="Days lookahead for bills due")


class BudgetStatusArgs(BaseModel):
    month: Optional[str] = Field(None, description="Month in YYYY-MM format")


class GoalStatusArgs(BaseModel):
    pass


class AnalyzePurchaseArgs(BaseModel):
    amount: float = Field(..., gt=0, description="Prospective purchase price in currency units")
    category: Optional[str] = Field("Shopping", description="Category of prospective purchase")


class SearchFinancialDocumentsArgs(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query for document retrieval")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Max document chunks to retrieve")
