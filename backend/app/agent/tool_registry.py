from typing import Any, Callable, Dict, List, Type
from pydantic import BaseModel

from app.agent.schemas import (
    AnalyzePurchaseArgs,
    BudgetStatusArgs,
    CategorySpendingArgs,
    GoalStatusArgs,
    MonthlySummaryArgs,
    RecurringPaymentsArgs,
    SearchFinancialDocumentsArgs,
    TransactionsArgs,
    UpcomingObligationsArgs,
)


class ToolDefinition:
    """Descriptor for an agent-callable tool."""

    def __init__(
        self,
        name: str,
        description: str,
        args_schema: Type[BaseModel],
    ):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema(),
        }


class ToolRegistry:
    """Registry maintaining the 9 required financial and RAG tools."""

    _tools: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, tool: ToolDefinition) -> None:
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> ToolDefinition:
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        return cls._tools[name]

    @classmethod
    def list_tools(cls) -> List[ToolDefinition]:
        return list(cls._tools.values())

    @classmethod
    def get_definitions_prompt(cls) -> str:
        """Formats concise tool descriptions for Qwen1.5-1B-Instruct."""
        lines = ["Available tools (output JSON with action='tool' and tool='<name>'):"]
        for tool in cls._tools.values():
            props = tool.args_schema.model_json_schema().get("properties", {})
            keys = list(props.keys())
            arg_str = ", ".join(keys) if keys else "none"
            lines.append(f"- {tool.name}: {tool.description}. Arguments: [{arg_str}]")
        return "\n".join(lines)


# Register the 9 core tools
ToolRegistry.register(
    ToolDefinition(
        name="get_monthly_summary",
        description="Retrieve monthly income, expenses, and net cashflow summary",
        args_schema=MonthlySummaryArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_transactions",
        description="Retrieve recent financial transactions filtered by category or type",
        args_schema=TransactionsArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_category_spending",
        description="Retrieve breakdown of spending by category with percentages",
        args_schema=CategorySpendingArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_recurring_payments",
        description="Retrieve detected active recurring subscriptions and frequencies",
        args_schema=RecurringPaymentsArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_upcoming_obligations",
        description="Project upcoming payment obligations and due dates within a day window",
        args_schema=UpcomingObligationsArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_budget_status",
        description="Retrieve user budgets, current spending, and track status (ON_TRACK, OVER_BUDGET)",
        args_schema=BudgetStatusArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="get_goal_status",
        description="Retrieve active savings goals, target amounts, current saved, and monthly required",
        args_schema=GoalStatusArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="analyze_purchase",
        description="Simulate prospective purchase scenario balance and financial buffer impact",
        args_schema=AnalyzePurchaseArgs,
    )
)
ToolRegistry.register(
    ToolDefinition(
        name="search_financial_documents",
        description="Perform semantic search on uploaded financial statement text and return source evidence",
        args_schema=SearchFinancialDocumentsArgs,
    )
)
