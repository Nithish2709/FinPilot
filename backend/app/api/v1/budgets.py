from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import BudgetCreate, BudgetStatusResponse, BudgetUpdate
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post(
    "",
    response_model=BudgetStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new budget",
)
async def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BudgetStatusResponse:
    return await FinancialService.create_budget(db, user_id=current_user.id, data=data)


@router.get(
    "",
    response_model=List[BudgetStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="List all user budgets with status",
)
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[BudgetStatusResponse]:
    return await FinancialService.get_budgets(db, user_id=current_user.id)


@router.get(
    "/{budget_id}",
    response_model=BudgetStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get budget details and status by ID",
)
async def get_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BudgetStatusResponse:
    budget = await FinancialService.get_budget_by_id(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or does not belong to authenticated user.",
        )
    return budget


@router.put(
    "/{budget_id}",
    response_model=BudgetStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing budget",
)
async def update_budget(
    budget_id: uuid.UUID,
    data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BudgetStatusResponse:
    updated = await FinancialService.update_budget(db, budget_id, current_user.id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or does not belong to authenticated user.",
        )
    return updated


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a budget",
)
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await FinancialService.delete_budget(db, budget_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or does not belong to authenticated user.",
        )
    return None
