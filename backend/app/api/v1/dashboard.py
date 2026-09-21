from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import DashboardResponse
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user financial dashboard summary",
    description="Calculates deterministic cashflow totals, top categories, upcoming obligations, and goal progress strictly scoped to authenticated user.",
)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    return await FinancialService.get_dashboard(db, user_id=current_user.id)
