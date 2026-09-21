from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import (
    AnalyticsResponse,
    CashFlowSummary,
    CategoryBreakdownResponse,
    UnusualSpendingResponse,
)
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated financial analytics",
    description="Returns aggregate cashflow, categories, recurring commitments, obligations, and anomalies.",
)
async def get_full_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    categories = await FinancialService.get_category_breakdown(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    unusual = await FinancialService.get_unusual_spending(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    obligations = await FinancialService.get_obligations(db, user_id=current_user.id, days_ahead=30)
    subs = await FinancialService.get_subscriptions(db, user_id=current_user.id)

    total_committed = sum(float(s.average_amount) for s in subs)
    txns = await FinancialService.get_dashboard(db, user_id=current_user.id)

    return AnalyticsResponse(
        cashflow=CashFlowSummary(
            start_date=start_date,
            end_date=end_date,
            total_income=txns.monthly_income,
            total_expenses=txns.monthly_expenses,
            total_refunds=txns.monthly_refunds,
            net_cashflow=txns.net_cashflow,
            transaction_count=txns.transaction_count,
        ),
        categories=categories,
        recurring={
            "total_monthly_committed": total_committed,
            "active_subscriptions_count": len(subs),
            "subscriptions": [s.model_dump() for s in subs],
        },
        obligations=obligations,
        unusual_spending=unusual,
    )


@router.get(
    "/categories",
    response_model=CategoryBreakdownResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category spending breakdown",
    description="Deterministic category aggregation and percentages. Transactions without categories are categorized via keyword rules or marked 'Uncategorized'.",
)
async def get_categories_breakdown(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CategoryBreakdownResponse:
    return await FinancialService.get_category_breakdown(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )


@router.get(
    "/unusual-spending",
    response_model=UnusualSpendingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detected unusual spending",
    description="Deterministic anomaly detection comparing current period spending against historical monthly averages. Does not use AI.",
)
async def get_unusual_spending_endpoint(
    start_date: Optional[date] = Query(None, description="Start date of current period"),
    end_date: Optional[date] = Query(None, description="End date of current period"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnusualSpendingResponse:
    return await FinancialService.get_unusual_spending(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
