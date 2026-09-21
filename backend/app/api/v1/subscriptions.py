from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import ObligationsResponse, RecurringPaymentResponse
from app.services.financial_service import FinancialService

router = APIRouter(tags=["Subscriptions & Obligations"])


@router.get(
    "/subscriptions",
    response_model=List[RecurringPaymentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get detected recurring subscriptions",
    description="Returns detected recurring payments based on deterministic frequency and amount consistency heuristics.",
)
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[RecurringPaymentResponse]:
    return await FinancialService.get_subscriptions(db, user_id=current_user.id)


@router.get(
    "/obligations",
    response_model=ObligationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get upcoming recurring obligations",
    description="Forecasts upcoming recurring payments due in the requested window (default 30 days).",
)
async def list_obligations(
    days_ahead: int = Query(30, ge=1, le=365, description="Lookahead window in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ObligationsResponse:
    return await FinancialService.get_obligations(db, user_id=current_user.id, days_ahead=days_ahead)
