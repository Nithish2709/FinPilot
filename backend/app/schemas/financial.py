from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


# -------------------------------------------------------------
# Cashflow & Dashboard Schemas
# -------------------------------------------------------------

class CashFlowSummary(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_income: Decimal = Decimal("0.00")
    total_expenses: Decimal = Decimal("0.00")
    total_refunds: Decimal = Decimal("0.00")
    net_cashflow: Decimal = Decimal("0.00")
    transaction_count: int = 0


class DataQualityInfo(BaseModel):
    source: str = "transaction_history"
    coverage: str = "available_period"
    note: str = "Calculations reflect available statement history without speculative opening balances."


class DashboardResponse(BaseModel):
    current_balance: Decimal
    balance_basis: str = "net_cashflow_from_history"
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_refunds: Decimal
    net_cashflow: Decimal
    transaction_count: int
    top_categories: List[Dict[str, Any]]
    upcoming_obligations: List[Dict[str, Any]]
    goal_progress: List[Dict[str, Any]]
    data_quality: DataQualityInfo


# -------------------------------------------------------------
# Category Breakdown Schemas
# -------------------------------------------------------------

class CategorySummaryItem(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal
    transaction_count: int


class CategoryBreakdownResponse(BaseModel):
    total_expenses: Decimal
    categories: List[CategorySummaryItem]


# -------------------------------------------------------------
# Recurring Payments & Obligations Schemas
# -------------------------------------------------------------

class RecurringPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant: str
    average_amount: Decimal
    frequency: str
    last_payment_date: date
    next_expected_date: Optional[date] = None
    confidence: Decimal
    status: str
    created_at: datetime


class ObligationItem(BaseModel):
    merchant: str
    expected_amount: Decimal
    expected_date: date
    frequency: str
    confidence: Decimal
    label: str = "Expected recurring obligation"


class ObligationsResponse(BaseModel):
    days_ahead: int
    total_obligations: Decimal
    obligations: List[ObligationItem]


# -------------------------------------------------------------
# Anomaly / Unusual Spending Schemas
# -------------------------------------------------------------

class UnusualSpendingItem(BaseModel):
    category: str
    current_amount: Decimal
    historical_average: Decimal
    difference: Decimal
    percentage_change: Decimal
    severity: str  # LOW, MEDIUM, HIGH
    explanation: str


class UnusualSpendingResponse(BaseModel):
    has_sufficient_history: bool
    historical_months_available: int
    anomalies: List[UnusualSpendingItem]


class AnalyticsResponse(BaseModel):
    cashflow: CashFlowSummary
    categories: CategoryBreakdownResponse
    recurring: Dict[str, Any]
    obligations: ObligationsResponse
    unusual_spending: UnusualSpendingResponse


# -------------------------------------------------------------
# Budget Schemas
# -------------------------------------------------------------

class BudgetCreate(BaseModel):
    name: str
    category: str
    amount: Decimal = Field(..., gt=0)
    period: str = "monthly"
    start_date: date
    end_date: Optional[date] = None


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    period: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str
    amount: Decimal
    period: str
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BudgetStatusResponse(BudgetResponse):
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
    status: str  # ON_TRACK, NEAR_LIMIT, OVER_BUDGET


# -------------------------------------------------------------
# Goal Schemas
# -------------------------------------------------------------

class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal = Field(..., gt=0)
    current_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    target_date: Optional[date] = None


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[Decimal] = Field(None, gt=0)
    current_amount: Optional[Decimal] = Field(None, ge=0)
    target_date: Optional[date] = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GoalProgressResponse(GoalResponse):
    remaining_amount: Decimal
    percentage_complete: Decimal
    required_monthly_saving: Optional[Decimal] = None
    is_completed: bool


# -------------------------------------------------------------
# Purchase Scenario Schemas
# -------------------------------------------------------------

class PurchaseAnalysisRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    purchase_date: Optional[date] = None
    description: Optional[str] = None
    safety_buffer: Optional[Decimal] = Field(default=Decimal("15000.00"), ge=0)


class ScenarioDetail(BaseModel):
    projected_balance: Decimal
    buffer_difference: Decimal


class PurchaseAnalysisResponse(BaseModel):
    current_balance: Decimal
    upcoming_obligations: Decimal
    purchase_amount: Decimal
    safety_buffer: Decimal
    projected_balance: Decimal
    buffer_difference: Decimal
    scenarios: Dict[str, ScenarioDetail]
    disclaimer: str = "Scenario calculations are mathematical projections and do not constitute financial advice or subjective recommendations."
