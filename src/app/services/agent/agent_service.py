# src/app/services/agent/agent_service.py
from typing import Any

from src.app.config import get_ollama_model
from src.app.conversation_store import (
    create_message,
    get_conversation,
    list_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.services.agent.loop import AgentLoop
from src.app.services.agent.prompt_builder import AgentPromptBuilder
from src.app.services.agent.state import AgentState
from src.app.services.llm.ollama_provider import OllamaProvider
from src.app.services.tools.registry import ToolRegistry
from src.app.services.tools.list_docs import ListDocsTool
from src.app.services.tools.search_docs import SearchDocsTool
from src.app.services.tools.read_doc import ReadDocTool


class AgentService:
    def __init__(self) -> None:
        self.llm_provider = OllamaProvider()
        self.prompt_builder = AgentPromptBuilder()

        registry = ToolRegistry()
        registry.register(ListDocsTool())
        registry.register(SearchDocsTool())
        registry.register(ReadDocTool())

        self.agent_loop = AgentLoop(tool_registry=registry)

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

        selected_model = model or conversation.get("model") or get_ollama_model()

        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=clean_question,
            metadata={
                "type": "agent_user_question",
            },
        )

        recent_messages = list_messages(conversation_id)[-10:]

        state = AgentState(
            conversation_id=conversation_id,
            user_message_id=user_message["id"],
            question=clean_question,
            messages=recent_messages,
            max_steps=max_steps,
            model=selected_model,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        state = self.agent_loop.run(state)

        final_messages = self.prompt_builder.build_final_messages(state)

        response = self.llm_provider.chat(
            messages=final_messages,
            model=selected_model,
        )

        tool_calls = [
            step.model_dump() for step in state.steps if step.type == "tool_call"
        ]

        trace = {
            "max_steps": max_steps,
            "step_count": len(state.steps),
            "used_tools": [step.tool_name for step in state.steps if step.tool_name],
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
                "tool_calls": tool_calls,
                "trace": trace,
                "model": response.model,
                "provider": response.provider,
            },
        )

        update_conversation(conversation_id, {})

        return {
            "conversation_id": conversation_id,
            "question": clean_question,
            "answer": assistant_message["content"],
            "tool_calls": tool_calls,
            "trace": trace,
        }
