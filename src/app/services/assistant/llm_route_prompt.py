from typing import Any


def build_route_messages(
    *,
    message: str,
    recent_messages: list[dict[str, Any]],
    recent_message_count: int = 6,
    options: dict[str, Any],
) -> list[dict[str, str]]:
    system = """
你是 NexusAI 的模式路由器。你的任务是判断用户当前问题应该进入哪种模式。

可选模式：
- chat：普通聊天、概念解释、无需知识库、无需工具。
- agent：需要知识库、文档资料或多步工具调用，例如先检索再读取文档，再总结、生成、对比、分析。
- mcp：需要外部系统或外部工具，例如 GitHub、浏览器、飞书、邮件、日历等。

你必须只输出 JSON，不要输出 Markdown，不要解释过程。

输出格式：
{
    "mode": "chat|agent|mcp",
    "confidence": 0.0,
    "reason": "不超过100字的原因",
    "should_rewrite_query": true,
    "retrieval_mode": "hybrid|null",
    "enable_rerank": true,
    "enable_mcp_tools": false
}

约束：
1. 不确定且无需知识库和工具时优先 chat，不要滥用 agent。
2. 用户明确说“根据知识库/文档/资料”时必须选择 agent。
3. 用户需要多步读取、分析多个文档、生成方案时选择 agent。
4. 只有需要外部系统时才 mcp。
5. 不要输出 chain-of-thought。
""".strip()

    user = f"""
【当前用户输入】
{message}

【最近消息】
{recent_messages[-recent_message_count:]}

【请求选项】
{options}

请输出 RouteDecision JSON：
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
