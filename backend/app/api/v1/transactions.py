from datetime import date
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionListResponse, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions",
    description="Lists user transactions with pagination and optional filtering by date, category, type, and account. Always strictly scoped to authenticated user.",
)
async def list_transactions(
    start_date: Optional[date] = Query(None, description="Filter transactions on or after this date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter transactions on or before this date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category substring"),
    transaction_type: Optional[str] = Query(None, description="Filter by type (DEBIT, CREDIT, REFUND, TRANSFER)"),
    account_id: Optional[uuid.UUID] = Query(None, description="Filter by account ID"),
    limit: int = Query(50, ge=1, le=200, description="Page limit (max 200)"),
    offset: int = Query(0, ge=0, description="Page offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    items, total = await TransactionRepository.get_by_user_filtered(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        transaction_type=transaction_type,
        account_id=account_id,
        limit=limit,
        offset=offset,
    )

    response_items = [TransactionResponse.model_validate(t) for t in items]
    return TransactionListResponse(
        items=response_items,
        total=total,
        limit=limit,
        offset=offset,
    )
