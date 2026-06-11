from typing import Any

from src.app.config import get_context_context_token_by_config
from src.app.services.agent.state import AgentState
from src.app.services.context_engineering.context_assembler import ContextAssembler
from src.app.services.context_engineering.schemas import (
    ContextBuildRequest,
    ContextPackage,
)


class AgentPromptBuilder:
    def __init__(self) -> None:
        self.context_assembler = ContextAssembler()

    def build_final_context_package(
        self,
        *,
        state: AgentState,
        conversation_summary: str | None,
        conversation_state: dict[str, Any] | None,
        long_term_memory_items: list[Any],
        max_context_tokens: int | None = None,
    ) -> ContextPackage:
        tool_steps = [step.model_dump(mode="json") for step in state.steps]
        observations = [item.model_dump(mode="json") for item in state.observations]

        return self.context_assembler.build(
            ContextBuildRequest(
                conversation_id=state.conversation_id,
                user_message=state.question,
                mode="agent",
                conversation_summary=conversation_summary,
                conversation_state=conversation_state,
                recent_messages=state.messages,
                long_term_memory_items=long_term_memory_items,
                working_memory=state.working_memory.model_dump(mode="json"),
                tool_observations=observations,
                tool_steps=tool_steps,
                output_requirement="请基于工具观察结果和可用上下文回答用户问题。回答要结构化，不能编造资料中不存在的信息。",
                max_context_tokens=(
                    max_context_tokens or get_context_context_token_by_config()
                ),
            )
        )

    def build_final_messages(self, state: AgentState) -> list[dict[str, str]]:
        """兼容旧调用。

        后续代码应优先使用 build_final_context_package()。
        """
        context_package = self.build_final_context_package(
            state=state,
            conversation_summary=None,
            conversation_state=None,
            long_term_memory_items=[],
        )
        return context_package.messages
