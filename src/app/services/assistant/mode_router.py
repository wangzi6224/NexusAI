from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.app.services.assistant.route_decision import RouteDecision


@dataclass(frozen=True)
class RouterContext:
    conversation_id: str
    message: str
    recent_messages: list[dict[str, Any]]
    options: dict[str, Any]


class RuleBasedModeRouter:
    """第一层确定性路由。

    生产原则：
    - 高置信度场景不调用 LLM:
    - 1. 高确定性请求
    - 2. 高风险请求
    - 3. 高频请求
    - 4. 成本敏感请求
    - 5. 明确指定模式的请求
    - 模糊场景返回 None，交给 LLM Router；
    - 规则要少而准，不要堆成不可维护的 if-else 海洋。
    """

    def route(self, context: RouterContext) -> RouteDecision | None:
        """根据上下文进行规则路由。

        Args:
            context (RouterContext): 路由上下文

        Returns:
            RouteDecision | None: 路由决策结果，如果无法确定则返回 None
        """
        text = context.message.strip().lower()

        if not text:
            return RouteDecision(
                mode="chat",
                confidence=1.0,
                source="rule",
                reason="空输入或无有效内容，按普通聊天处理",
            )

        if self._is_small_talk(text):
            return RouteDecision(
                mode="chat",
                confidence=0.95,
                source="rule",
                reason="用户是普通闲聊或问候，不需要检索和工具调用",
            )

        if self._is_explicit_rag(text):
            return RouteDecision(
                mode="rag",
                confidence=0.95,
                source="rule",
                reason="用户明确要求根据知识库、文档或资料回答",
                should_rewrite_query=True,
                retrieval_mode=context.options.get("retrieval_mode") or "hybrid",
                enable_rerank=context.options.get("enable_rerank", True),
            )

        if self._is_explicit_agent(text):
            return RouteDecision(
                mode="agent",
                confidence=0.9,
                source="rule",
                reason="用户请求需要多步检索、读取、分析或生成，适合 Agent 模式",
            )

        if self._is_explicit_mcp(text):
            return RouteDecision(
                mode="mcp",
                confidence=0.9,
                source="rule",
                reason="用户请求涉及外部工具或外部系统，适合 MCP 工具模式",
                enable_mcp_tools=True,
            )

        return None

    # 以下是一些简单的启发式规则示例，实际生产中可以根据需求调整和优化。
    def _is_small_talk(self, text: str) -> bool:
        keywords = ["你好", "hello", "hi", "谢谢", "thanks", "你是谁", "介绍一下你"]
        return any(item in text for item in keywords)

    # 下面的规则示例仅供参考，实际生产中需要根据具体业务场景和用户输入特点进行调整和优化。
    def _is_explicit_rag(self, text: str) -> bool:
        keywords = [
            "根据知识库",
            "根据文档",
            "根据资料",
            "结合知识库",
            "结合文档",
            "知识库里",
            "文档里",
            "规范里",
        ]
        return any(item in text for item in keywords)

    # Agent 模式适合需要多步推理、检索、分析或生成的复杂任务，不是所有“生成”都走 Agent。
    def _is_explicit_agent(self, text: str) -> bool:
        # Agent 适合多步任务，不是所有“生成”都走 Agent。
        task_keywords = [
            "帮我分析",
            "帮我生成",
            "整理方案",
            "对比",
            "总结所有",
            "读取",
            "列出文档",
        ]
        multi_step_keywords = ["多个文档", "完整", "详细", "先", "然后", "再", "一步步"]
        return any(k in text for k in task_keywords) and any(
            k in text for k in multi_step_keywords
        )

    # MCP 模式适合明确涉及外部工具调用的场景，如查询日历、发送邮件、访问数据库等。
    def _is_explicit_mcp(self, text: str) -> bool:
        keywords = [
            "外部工具",
            "mcp",
            "github",
            "网页",
            "浏览器",
            "飞书",
            "邮件",
            "日历",
        ]
        return any(item in text for item in keywords)
