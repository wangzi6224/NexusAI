from typing import Any
from time import perf_counter

from src.app.document_store import get_document
from src.app.services.tools.base import Tool
from src.app.services.tools.result import tool_error, tool_success


class ReadDocTool(Tool):
    name = "read_doc"
    description = "读取指定文档的内容。适用于用户明确要求查看某个文档，或需要基于完整文档继续分析。"
    parameters = {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "文档 ID",
            },
            "max_chars": {
                "type": "integer",
                "description": "最多返回多少字符，避免上下文过长",
                "default": 6000,
                "minimum": 500,
                "maximum": 20000,
            },
        },
        "required": ["document_id"],
        "additionalProperties": False,
    }

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        start = perf_counter()
        document_id = str(arguments.get("document_id", "")).strip()

        if not document_id:
            return tool_error(
                tool_name=self.name,
                code="INVALID_ARGUMENTS",
                message="document_id 不能为空",
                latency_ms=int((perf_counter() - start) * 1000),
            )

        max_chars = int(arguments.get("max_chars", 6000))
        max_chars = max(500, min(max_chars, 20000))

        document = get_document(document_id)

        if document is None:
            return tool_error(
                tool_name=self.name,
                code="DOCUMENT_NOT_FOUND",
                message="文档不存在",
                latency_ms=int((perf_counter() - start) * 1000),
                metadata={"document_id": document_id},
            )

        content = str(document.get("content") or "")
        truncated = len(content) > max_chars
        returned_content = content[:max_chars]

        return tool_success(
            tool_name=self.name,
            data={
                "document_id": document["id"],
                "filename": document["filename"],
                "content": returned_content,
                "char_count": len(content),
                "returned_char_count": len(returned_content),
                "truncated": truncated,
            },
            latency_ms=int((perf_counter() - start) * 1000),
            metadata={
                "document_id": document_id,
                "max_chars": max_chars,
                "truncated": truncated,
            },
        )
