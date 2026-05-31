from __future__ import annotations

from src.app.schemas.assistant import AssistantStreamRequest, RouteDecision


class ModeRouter:
    """Assistant mode 路由器。

    Week 14 只做规则版：
    - 不需要工具：chat
    - 需要知识库 / 文档 / 工具：agent

    Week 16 再升级 LLM Router。
    """

    AGENT_KEYWORDS = [
        "根据知识库",
        "知识库",
        "根据文档",
        "文档",
        "有哪些文档",
        "文档列表",
        "查一下",
        "查询",
        "检索",
        "读取",
        "完整内容",
        "规范",
        "组件模板",
        "总结文档",
        "对比文档",
        "分析文档",
    ]

    def route(self, request: AssistantStreamRequest) -> RouteDecision:
        if request.mode == "chat":
            return RouteDecision(
                mode="chat",
                reason="用户手动选择 chat 模式",
            )

        if request.mode == "agent":
            return RouteDecision(
                mode="agent",
                reason="用户手动选择 agent 模式",
            )

        message = request.message.strip()

        if not request.options.enable_tools:
            return RouteDecision(
                mode="chat",
                reason="options.enable_tools=false，禁用工具调用",
            )

        matched = [keyword for keyword in self.AGENT_KEYWORDS if keyword in message]

        if matched:
            return RouteDecision(
                mode="agent",
                reason="问题命中知识库、文档或工具调用关键词，需要进入 Agent 工具链路",
                matched_keywords=matched,
            )

        return RouteDecision(
            mode="chat",
            reason="问题未命中工具类关键词，使用普通聊天链路",
        )
