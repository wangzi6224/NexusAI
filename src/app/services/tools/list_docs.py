from typing import Any
from time import perf_counter

from src.app.document_store import list_documents
from src.app.services.tools.base import Tool
from src.app.services.tools.result import tool_success


class ListDocsTool(Tool):
    name = "list_docs"
    description = (
        "列出当前知识库中的文档。适用于用户询问有哪些文档、知识库包含什么资料。"
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        start = perf_counter()
        documents = list_documents()
        latency_ms = int((perf_counter() - start) * 1000)

        return tool_success(
            tool_name=self.name,
            data={
                "documents": [
                    {
                        "document_id": item["id"],
                        "filename": item["filename"],
                        "status": item.get("status"),
                        "created_at": item.get("created_at"),
                    }
                    for item in documents
                ]
            },
            latency_ms=latency_ms,
            metadata={"document_count": len(documents)},
        )
