from typing import Any

from src.app.services.tools.base import Tool
from src.app.services.rag.retriever import RagRetriever


class SearchDocsTool(Tool):
    name = "search_docs"
    description = (
        "根据用户问题检索知识库文档片段。"
        "适用于需要根据企业规范、项目文档、组件规范、技术文档回答的问题。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "用于知识库检索的完整问题或关键词",
            },
            "top_k": {
                "type": "integer",
                "description": "最多返回多少个相关 chunk",
                "default": 5,
            },
            "score_threshold": {
                "type": "number",
                "description": "最低相关性分数",
                "default": 0.3,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }

    def __init__(self) -> None:
        self.retriever = RagRetriever()

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).strip()

        if not query:
            return {
                "success": False,
                "tool_name": self.name,
                "error": {
                    "code": "INVALID_ARGUMENTS",
                    "message": "query 不能为空",
                },
            }

        top_k = int(arguments.get("top_k", 5))
        score_threshold = float(arguments.get("score_threshold", 0.3))

        result = self.retriever.search(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        return {
            "success": True,
            "tool_name": self.name,
            "data": result,
        }
