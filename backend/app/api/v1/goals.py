from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import GoalCreate, GoalProgressResponse, GoalUpdate
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post(
    "",
    response_model=GoalProgressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new savings goal",
)
async def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalProgressResponse:
    return await FinancialService.create_goal(db, user_id=current_user.id, data=data)


@router.get(
    "",
    response_model=List[GoalProgressResponse],
    status_code=status.HTTP_200_OK,
    summary="List all user goals with progress tracking",
)
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[GoalProgressResponse]:
    return await FinancialService.get_goals(db, user_id=current_user.id)


@router.get(
    "/{goal_id}",
    response_model=GoalProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get goal details and progress by ID",
)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalProgressResponse:
    goal = await FinancialService.get_goal_by_id(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or does not belong to authenticated user.",
        )
    return goal


@router.put(
    "/{goal_id}",
    response_model=GoalProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a savings goal",
)
async def update_goal(
    goal_id: uuid.UUID,
    data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalProgressResponse:
    updated = await FinancialService.update_goal(db, goal_id, current_user.id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or does not belong to authenticated user.",
        )
    return updated


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a savings goal",
)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await FinancialService.delete_goal(db, goal_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or does not belong to authenticated user.",
        )
    return None
