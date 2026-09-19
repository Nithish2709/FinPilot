from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.chat import router as chat_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.documents import router as documents_router
from app.api.v1.goals import router as goals_router
from app.api.v1.health import router as health_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.transactions import router as transactions_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(subscriptions_router)
api_v1_router.include_router(budgets_router)
api_v1_router.include_router(goals_router)
api_v1_router.include_router(purchases_router)
api_v1_router.include_router(chat_router)


