from pathlib import Path
from typing import Any

from fastapi import UploadFile

from src.app.document_store import (
    create_document,
    create_document_chunks,
    delete_document,
    delete_document_chunks,
    get_document,
    list_document_chunks,
    list_documents,
    update_document,
)
from src.app.exceptions import AppError
from src.app.services.chunk_splitter import ChunkSplitter
from src.app.services.document_loader import DocumentLoader


class DocumentService:
    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.splitter = ChunkSplitter()

    async def upload_document(self, file: UploadFile) -> dict[str, Any]:
        filename = file.filename or ""

        document: dict[str, Any] | None = None

        try:
            content_bytes = await file.read()

            file_type = self.loader.validate_file(
                filename=filename,
                content=content_bytes,
            )

            text = self.loader.load_text(
                filename=filename,
                content=content_bytes,
            )

            saved_path = self.loader.save_upload_file(
                filename=filename,
                content=content_bytes,
            )

            document = create_document(
                filename=filename,
                file_type=file_type,
                source_path=str(saved_path),
                content=text,
                status="processing",
            )

            chunk_drafts = self.splitter.split(
                text=text,
                file_type=file_type,
            )

            if not chunk_drafts:
                raise AppError(
                    code="DOCUMENT_CHUNK_EMPTY",
                    message="文档没有生成有效 Chunk",
                    status_code=400,
                )

            chunk_records = create_document_chunks(
                document_id=document["id"],
                chunks=chunk_drafts,
            )

            updated_document = update_document(
                document["id"],
                {
                    "status": "completed",
                    "chunk_count": len(chunk_records),
                    "char_count": len(text),
                    "error_message": None,
                },
            )

            return {
                "document_id": updated_document["id"],
                "filename": updated_document["filename"],
                "file_type": updated_document["file_type"],
                "status": updated_document["status"],
                "chunk_count": updated_document["chunk_count"],
                "char_count": updated_document["char_count"],
                "created_at": updated_document["created_at"],
            }

        except Exception as exc:
            if document is not None:
                update_document(
                    document["id"],
                    {
                        "status": "failed",
                        "error_message": str(exc),
                    },
                )

            raise

    def list_documents(self) -> list[dict[str, Any]]:
        documents = list_documents()

        return [self._without_content(document) for document in documents]

    def get_document_detail(self, document_id: str) -> dict[str, Any]:
        document = get_document(document_id)

        if document is None:
            raise AppError(
                code="DOCUMENT_NOT_FOUND",
                message="文档不存在",
                detail=f"document_id={document_id}",
                status_code=404,
            )

        return document

    def get_document_chunks(self, document_id: str) -> list[dict[str, Any]]:
        document = get_document(document_id)

        if document is None:
            raise AppError(
                code="DOCUMENT_NOT_FOUND",
                message="文档不存在",
                detail=f"document_id={document_id}",
                status_code=404,
            )

        return list_document_chunks(document_id)

    def delete_document(self, document_id: str) -> dict[str, Any]:
        document = get_document(document_id)

        if document is None:
            raise AppError(
                code="DOCUMENT_NOT_FOUND",
                message="文档不存在",
                detail=f"document_id={document_id}",
                status_code=404,
            )

        source_path = document.get("source_path")
        if source_path:
            path = Path(source_path)
            if path.exists() and path.is_file():
                path.unlink()

        delete_document_chunks(document_id)
        delete_document(document_id)

        return {
            "success": True,
            "message": "文档已删除",
        }

    def _without_content(self, document: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in document.items() if key != "content"}
