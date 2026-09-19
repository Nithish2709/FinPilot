from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import PurchaseAnalysisRequest, PurchaseAnalysisResponse
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post(
    "/analyze",
    response_model=PurchaseAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze purchase scenarios",
    description="Calculates impact on projected balance and safety buffer under 'purchase now' and 'wait' scenarios. Does NOT offer subjective buy/don't buy recommendations.",
)
async def analyze_purchase_scenario(
    req: PurchaseAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseAnalysisResponse:
    return await FinancialService.analyze_purchase(db, user_id=current_user.id, req=req)
