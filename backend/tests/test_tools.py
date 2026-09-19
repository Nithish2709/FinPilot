import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry


def test_tool_registry_contains_nine_tools():
    tools = ToolRegistry.list_tools()
    assert len(tools) == 9
    names = {t.name for t in tools}
    expected = {
        "get_monthly_summary",
        "get_transactions",
        "get_category_spending",
        "get_recurring_payments",
        "get_upcoming_obligations",
        "get_budget_status",
        "get_goal_status",
        "analyze_purchase",
        "search_financial_documents",
    }
    assert expected.issubset(names)


@pytest.mark.asyncio
async def test_tool_executor_unknown_tool(client):
    from tests.conftest import TestingSessionLocal
    fake_user = uuid.uuid4()
    async with TestingSessionLocal() as db:
        with pytest.raises(KeyError):
            await ToolExecutor.execute(
                db=db,
                user_id=fake_user,
                tool_name="non_existent_tool",
                arguments={},
            )


@pytest.mark.asyncio
async def test_tool_executor_purchase_analysis(client):
    from tests.conftest import TestingSessionLocal
    fake_user = uuid.uuid4()
    async with TestingSessionLocal() as db:
        res = await ToolExecutor.execute(
            db=db,
            user_id=fake_user,
            tool_name="analyze_purchase",
            arguments={"amount": 25000, "category": "Electronics"},
        )
        assert res["success"] is True
        assert res["tool"] == "analyze_purchase"
        assert "data" in res
