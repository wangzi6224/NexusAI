from typing import Any


class RuleBasedPlanner:
    """
    第一版 Agent 决策器。

    目的：
    先用确定性规则跑通 Agent Loop。
    """

    def plan(self, question: str, step_count: int) -> dict[str, Any]:
        text = question.strip()

        if any(
            keyword in text for keyword in ["有哪些文档", "文档列表", "知识库里有什么"]
        ):
            return {
                "type": "tool_call",
                "tool_name": "list_docs",
                "arguments": {},
                "reason": "用户询问知识库文档列表",
            }

        if any(
            keyword in text
            for keyword in [
                "根据知识库",
                "根据文档",
                "规范",
                "查询",
                "检索",
                "组件模板",
            ]
        ):
            return {
                "type": "tool_call",
                "tool_name": "search_docs",
                "arguments": {
                    "query": text,
                    "top_k": 5,
                    "score_threshold": 0.3,
                },
                "reason": "用户问题需要基于知识库资料回答",
            }

        return {
            "type": "final",
            "reason": "当前问题不需要调用工具",
        }
