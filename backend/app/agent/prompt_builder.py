from typing import Dict, List, Optional

from app.agent.tool_registry import ToolRegistry
from app.schemas.chat import ConversationContextResponse


class PromptBuilder:
    """Constructs focused prompts for Qwen1.5-1B-Instruct."""

    SYSTEM_PROMPT = (
        "You are FinPilot, a personal finance information assistant.\n"
        "Your job is to understand the user's question and use available tools.\n\n"
        "Rules:\n"
        "1. Never invent financial data or calculate totals yourself.\n"
        "2. Use tools for financial facts, spending, budgets, and document search.\n"
        "3. Output ONLY valid JSON matching either:\n"
        '   {"action": "tool", "tool": "<tool_name>", "arguments": {...}}\n'
        "   OR\n"
        '   {"action": "final", "answer": "<your natural language explanation>"}\n'
        "4. Do not include markdown code blocks or text outside the JSON.\n"
        "5. Keep explanations concise, clear, and factual."
    )

    @classmethod
    def build_initial_messages(
        cls,
        user_message: str,
        context: Optional[ConversationContextResponse] = None,
    ) -> List[Dict[str, str]]:
        messages = []

        # System prompt with tool definitions
        tools_str = ToolRegistry.get_definitions_prompt()
        full_system = f"{cls.SYSTEM_PROMPT}\n\n{tools_str}"
        messages.append({"role": "system", "content": full_system})

        # Inject older conversation summary if available
        if context and context.summary:
            messages.append({
                "role": "system",
                "content": f"Prior conversation summary: {context.summary}"
            })

        # Inject recent chronological messages from context
        if context and context.recent_messages:
            for m in context.recent_messages:
                r = m.role.lower() if m.role.lower() in {"user", "assistant", "system"} else "user"
                messages.append({"role": r, "content": m.content})

        # Append current user prompt
        messages.append({"role": "user", "content": user_message})
        return messages
