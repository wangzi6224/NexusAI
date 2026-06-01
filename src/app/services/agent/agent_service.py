from typing import Any

from time import perf_counter

from src.app.agent_trace_store import (
    create_agent_event,
    create_agent_run,
    create_agent_step,
    update_agent_run,
)

from src.app.config import (
    get_llm_provider_name,
    resolve_llm_model,
    get_agent_planner_type,
)
from src.app.conversation_store import (
    create_message,
    get_conversation,
    list_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.services.agent.loop import AgentLoop
from src.app.services.agent.planner_prompt_builder import LLM_PLANNER_PROMPT_VERSION
from src.app.services.agent.prompt_builder import AgentPromptBuilder
from src.app.services.agent.state import AgentState
from src.app.services.assistant.event import EVENT_AGENT_RUN_END, EVENT_AGENT_RUN_START
from src.app.services.llm.factory import get_llm_provider
from src.app.services.tools.registry import ToolRegistry
from src.app.services.tools.list_docs import ListDocsTool
from src.app.services.tools.search_docs import SearchDocsTool
from src.app.services.tools.read_doc import ReadDocTool


class AgentService:
    def __init__(self) -> None:
        self.llm_provider = get_llm_provider()
        self.prompt_builder = AgentPromptBuilder()
        self.planner_type = get_agent_planner_type()

        registry = ToolRegistry()
        registry.register(ListDocsTool())
        registry.register(SearchDocsTool())
        registry.register(ReadDocTool())

        self.agent_loop = AgentLoop(
            tool_registry=registry,
            planner_type=self.planner_type,
        )

    def chat(
        self,
        conversation_id: str,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        max_steps: int = 3,
        model: str | None = None,
    ) -> dict[str, Any]:
        conversation = get_conversation(conversation_id)

        if conversation is None:
            raise ConversationError(
                message="会话不存在",
                detail=f"conversation_id={conversation_id}",
                status_code=404,
            )

        clean_question = question.strip()

        if not clean_question:
            raise ConversationError(
                message="问题不能为空",
                status_code=400,
            )

        selected_model = resolve_llm_model(
            model=model,
            stored_model=conversation.get("model"),
            stored_provider=conversation.get("provider"),
        )

        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=clean_question,
            metadata={
                "type": "agent_user_question",
            },
        )

        run_start = perf_counter()

        agent_run = create_agent_run(
            conversation_id=conversation_id,
            user_message_id=user_message["id"],
            input_text=clean_question,
            model=selected_model,
            provider=get_llm_provider_name(),
            max_steps=max_steps,
            metadata={
                "top_k": top_k,
                "score_threshold": score_threshold,
            },
        )

        run_id = agent_run["id"]

        create_agent_event(
            run_id=run_id,
            event_type=EVENT_AGENT_RUN_START,
            payload={
                "conversation_id": conversation_id,
                "user_message_id": user_message["id"],
                "question": clean_question,
                "model": selected_model,
            },
        )

        recent_messages = list_messages(conversation_id)[-10:]

        state = AgentState(
            run_id=run_id,
            conversation_id=conversation_id,
            user_message_id=user_message["id"],
            question=clean_question,
            messages=recent_messages,
            max_steps=max_steps,
            model=selected_model,
            top_k=top_k,
            score_threshold=score_threshold,
            planner_type=self.planner_type,
            planner_prompt_version=(
                LLM_PLANNER_PROMPT_VERSION
                if self.planner_type == "llm"
                else self.planner_type
            ),
        )

        state: AgentState = self.agent_loop.run(state)

        final_messages = self.prompt_builder.build_final_messages(state)

        final_answer_start = perf_counter()

        response = self.llm_provider.chat(
            messages=final_messages,
            model=selected_model,
        )

        final_answer_latency_ms = int((perf_counter() - final_answer_start) * 1000)

        create_agent_step(
            run_id=run_id,
            step_index=len(state.steps) + 1,
            step_type="final_answer",
            success=True,
            latency_ms=final_answer_latency_ms,
            tool_result={
                "answer": response.content,
                "model": response.model,
                "provider": response.provider,
            },
        )

        total_latency_ms = int((perf_counter() - run_start) * 1000)

        update_agent_run(
            run_id,
            status="completed",
            final_answer=response.content,
            step_count=len(state.steps) + 1,
            total_latency_ms=total_latency_ms,
        )

        create_agent_event(
            run_id=run_id,
            event_type=EVENT_AGENT_RUN_END,
            payload={
                "status": "completed",
                "step_count": len(state.steps) + 1,
                "total_latency_ms": total_latency_ms,
            },
        )

        tool_calls = [
            step.model_dump() for step in state.steps if step.type == "tool_call"
        ]

        trace = {
            "run_id": run_id,
            "max_steps": max_steps,
            "loop_step_count": len(state.steps),
            "tool_call_count": len(tool_calls),
            "used_tools": [step.tool_name for step in state.steps if step.tool_name],
            "finish_reason": state.finish_reason,
            "planner": {
                "type": state.planner_type,
                "prompt_version": state.planner_prompt_version,
                "fallback_count": state.planner_fallback_count,
                "decision_count": state.planner_decision_count,
            },
            "observations": [item.model_dump() for item in state.observations],
            "model": response.model,
            "provider": response.provider,
        }

        assistant_message = create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            metadata={
                "type": "agent_answer",
                "user_message_id": user_message["id"],
                "run_id": run_id,
                "tool_calls": tool_calls,
                "trace": trace,
                "model": response.model,
                "provider": response.provider,
            },
        )

        update_conversation(conversation_id, {})

        return {
            "run_id": run_id,
            "conversation_id": conversation_id,
            "user_message_id": user_message["id"],
            "assistant_message_id": assistant_message["id"],
            "question": clean_question,
            "answer": assistant_message["content"],
            "tool_calls": tool_calls,
            "trace": trace,
        }
