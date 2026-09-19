import json
import logging
import time
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_router import LLMRouter, RouterResult
from app.agent.prompt_builder import PromptBuilder
from app.agent.schemas import AgentFinalResponse
from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry
from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository
from app.services.context_service import ContextService

logger = logging.getLogger(__name__)


class AgentService:
    """
    Controlled tool-calling agent orchestrator with multi-provider reliability.
    Dispatches prompts through LLMRouter (Local Qwen primary with API fallback).
    """

    def __init__(self, router: Optional[LLMRouter] = None):
        self.router = router or LLMRouter()

    async def process_message(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        user_message: str,
    ) -> Dict[str, Any]:
        """
        Executes controlled agent loop for authenticated user and conversation.
        Returns:
            {
                "answer": str,
                "model_used": str,
                "metadata": dict
            }
        """
        start_time = time.time()

        # 1. Verify conversation ownership
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found or unauthorized for user {user_id}")

        # 2. Build Stage 5 conversation context
        context = await ContextService.build_conversation_context(db, conversation_id, user_id)

        # 3. Assemble prompt
        messages = PromptBuilder.build_initial_messages(user_message, context)

        tool_calls_record: List[Dict[str, Any]] = []
        max_calls = settings.MAX_TOOL_CALLS

        final_answer: Optional[str] = None
        last_route_res: Optional[RouterResult] = None
        call_count = 0

        while call_count < max_calls and not final_answer:
            call_count += 1

            # Dispatch via LLMRouter (handles local retries and API fallback)
            route_res: RouterResult = await self.router.route_request(messages)
            last_route_res = route_res
            parsed_json = route_res.parsed_json

            action = parsed_json.get("action")

            # Final explanation
            if action == "final" or "answer" in parsed_json:
                try:
                    final_obj = AgentFinalResponse.model_validate(parsed_json)
                    final_answer = final_obj.answer
                except Exception:
                    final_answer = parsed_json.get("answer", "Here is the information from your financial records.")
                break

            # Tool execution request
            elif action == "tool":
                tool_name = parsed_json.get("tool", "")
                arguments = parsed_json.get("arguments", {})

                # Validate tool is registered
                try:
                    ToolRegistry.get(tool_name)
                except KeyError:
                    logger.warning(f"Model requested unknown tool '{tool_name}'")
                    messages.append({
                        "role": "user",
                        "content": f"Error: Tool '{tool_name}' does not exist. Choose from the available tools or provide a final answer."
                    })
                    continue

                # Record tool call
                tool_calls_record.append({
                    "tool": tool_name,
                    "arguments": arguments,
                })

                # Execute tool strictly with authenticated user_id
                tool_exec_start = time.time()
                tool_result = await ToolExecutor.execute(
                    db=db,
                    user_id=user_id,
                    tool_name=tool_name,
                    arguments=arguments,
                )
                tool_latency = round(time.time() - tool_exec_start, 4)
                tool_calls_record[-1]["latency"] = tool_latency

                # Append tool result to context for explanation
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({"action": "tool", "tool": tool_name, "arguments": arguments})
                })
                messages.append({
                    "role": "user",
                    "content": f"TOOL EXECUTION RESULT for '{tool_name}': {json.dumps(tool_result)}. Now explain these findings clearly to the user in a final response."
                })

            else:
                final_answer = str(parsed_json)
                break

        if not final_answer:
            final_answer = "I completed the financial queries, but was unable to assemble the final explanation. Please check your dashboard."

        total_latency = round(time.time() - start_time, 4)

        provider_name = last_route_res.provider if last_route_res else "local"
        model_name = last_route_res.model if last_route_res else settings.LOCAL_LLM_MODEL
        model_identifier = f"{provider_name}:{model_name.lower()}"

        return {
            "answer": final_answer,
            "model_used": model_identifier,
            "metadata": {
                "provider": provider_name,
                "model": model_name,
                "fallback": last_route_res.fallback if last_route_res else False,
                "fallback_reason": last_route_res.fallback_reason.value if last_route_res and last_route_res.fallback_reason else None,
                "input_tokens": last_route_res.input_tokens if last_route_res else None,
                "output_tokens": last_route_res.output_tokens if last_route_res else None,
                "latency_ms": round(total_latency * 1000, 2),
                "tool_calls": tool_calls_record,
                "tool_count": len(tool_calls_record),
            },
        }
