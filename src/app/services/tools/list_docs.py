from typing import Any

from src.app.services.tools.base import Tool
from src.app.document_store import list_documents


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
        documents = list_documents()

        return {
            "success": True,
            "tool_name": self.name,
            "data": {
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
        }
