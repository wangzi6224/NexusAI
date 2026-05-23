from typing import Any

from src.app.services.tools.base import Tool
from src.app.document_store import get_document


class ReadDocTool(Tool):
    name = "read_doc"
    description = "读取指定文档的内容。适用于用户明确要求查看某个文档，或需要基于完整文档继续分析。"
    parameters = {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "文档 ID",
            }
        },
        "required": ["document_id"],
        "additionalProperties": False,
    }

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        document_id = str(arguments.get("document_id", "")).strip()

        if not document_id:
            return {
                "success": False,
                "tool_name": self.name,
                "error": {
                    "code": "INVALID_ARGUMENTS",
                    "message": "document_id 不能为空",
                },
            }

        document = get_document(document_id)

        if document is None:
            return {
                "success": False,
                "tool_name": self.name,
                "error": {
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": "文档不存在",
                },
            }

        return {
            "success": True,
            "tool_name": self.name,
            "data": {
                "document_id": document["id"],
                "filename": document["filename"],
                "content": document["content"],
            },
        }
