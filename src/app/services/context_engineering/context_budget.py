from collections import defaultdict

from src.app.services.context_engineering.schemas import ContextItem


class ContextBudget:
    def __init__(self, max_context_tokens: int = 327680) -> None:
        self.max_context_tokens = max_context_tokens

    def budget_for_type(self, item_type: str) -> int:
        ratios = {
            "system_instruction": 0.10,
            "safety_policy": 0.05,
            "conversation_summary": 0.08,
            "conversation_state": 0.07,
            "recent_message": 0.15,
            "long_term_memory": 0.15,
            "working_memory": 0.08,
            "tool_observation": 0.18,
            "retrieved_source": 0.12,
            "read_document": 0.10,
            "output_requirement": 0.02,
        }
        return int(self.max_context_tokens * ratios.get(item_type, 0.05))

    def select_with_budget(
        self, items: list[ContextItem]
    ) -> tuple[list[ContextItem], list[tuple[ContextItem, str]]]:
        """按类型预算选择上下文。

        返回：
        - selected：进入最终 ContextPackage 的 item
        - dropped：被丢弃的 item 和原因
        """

        # used_by_type 记录每种类型已使用的 token 数，total_used 记录总的 token 使用。
        used_by_type: dict[str, int] = defaultdict(int)

        # 总的 token 使用。
        total_used = 0

        # selected 和 dropped 分别记录被选中和被丢弃的 item。被丢弃的 item 还会附带一个字符串，说明丢弃原因（如 "over_budget" 或 "type_budget_exceeded"）。
        selected: list[ContextItem] = []
        dropped: list[tuple[ContextItem, str]] = []

        for item in items:
            if item.required:
                selected.append(item)
                used_by_type[item.type] += item.estimated_tokens
                total_used += item.estimated_tokens
                continue

            # type_budget = self.budget_for_type(item.type)
            next_type_used = used_by_type[item.type] + item.estimated_tokens
            next_total_used = total_used + item.estimated_tokens

            # TODO 临时注释掉预算限制，后续根据实际情况调整预算分配和限制策略。

            # if next_total_used > self.max_context_tokens:
            #     dropped.append((item, "over_budget"))
            #     continue

            # if next_type_used > type_budget:
            #     dropped.append((item, "type_budget_exceeded"))
            #     continue

            selected.append(item)
            used_by_type[item.type] = next_type_used
            total_used = next_total_used

        return selected, dropped
