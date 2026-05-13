import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.app.exceptions import AppError
from src.app.paths import DATA_DIR, DOCUMENTS_FILE, DOCUMENT_CHUNKS_FILE


def _now_iso() -> str:
    return datetime.now().isoformat()


def _ensure_json_file(path: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    _ensure_json_file(path)

    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            raise AppError(
                code="DOCUMENT_STORE_ERROR",
                message="JSON 存储格式错误",
                detail=f"{path} 内容不是数组",
                status_code=500,
            )

        return data

    except json.JSONDecodeError as exc:
        raise AppError(
            code="DOCUMENT_STORE_ERROR",
            message="读取 JSON 失败",
            detail=f"{path}: {exc}",
            status_code=500,
        ) from exc


def _save_json_list(path: Path, items: list[dict[str, Any]]) -> None:
    _ensure_json_file(path)

    try:
        path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise AppError(
            code="DOCUMENT_STORE_ERROR",
            message="写入 JSON 失败",
            detail=f"{path}: {exc}",
            status_code=500,
        ) from exc


def load_documents() -> list[dict[str, Any]]:
    return _load_json_list(DOCUMENTS_FILE)


def save_documents(documents: list[dict[str, Any]]) -> None:
    _save_json_list(DOCUMENTS_FILE, documents)


def create_document(
    filename: str,
    file_type: str,
    source_path: str,
    content: str,
    status: str = "pending",
    error_message: str | None = None,
) -> dict[str, Any]:
    now: str = _now_iso()

    document = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "file_type": file_type,
        "source_path": source_path,
        "content": content,
        "status": status,
        "chunk_count": 0,
        "char_count": len(content),
        "error_message": error_message,
        "created_at": now,
        "updated_at": now,
    }

    documents: list[dict[str, Any]] = load_documents()
    documents.append(document)
    save_documents(documents)

    return document


def update_document(
    document_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    documents: list[dict[str, Any]] = load_documents()

    for document in documents:
        if document["id"] == document_id:
            document.update(updates)
            document["updated_at"] = _now_iso()
            save_documents(documents)
            return document

    raise AppError(
        code="DOCUMENT_NOT_FOUND",
        message="文档不存在",
        detail=f"document_id={document_id}",
        status_code=404,
    )


def get_document(document_id: str) -> dict[str, Any] | None:
    documents = load_documents()

    for document in documents:
        if document["id"] == document_id:
            return document

    return None


def list_documents() -> list[dict[str, Any]]:
    documents = load_documents()
    return sorted(
        documents,
        key=lambda item: item.get("updated_at", ""),
        reverse=True,
    )


def delete_document(document_id: str) -> None:
    documents = load_documents()
    next_documents = [
        document for document in documents if document["id"] != document_id
    ]

    if len(next_documents) == len(documents):
        raise AppError(
            code="DOCUMENT_NOT_FOUND",
            message="文档不存在",
            detail=f"document_id={document_id}",
            status_code=404,
        )

    save_documents(next_documents)


def load_document_chunks() -> list[dict[str, Any]]:
    return _load_json_list(DOCUMENT_CHUNKS_FILE)


def save_document_chunks(chunks: list[dict[str, Any]]) -> None:
    _save_json_list(DOCUMENT_CHUNKS_FILE, chunks)


def create_document_chunks(
    document_id: str,
    chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    now = _now_iso()

    records: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        content = chunk.get("content", "").strip()
        if not content:
            continue

        record = {
            "id": str(uuid.uuid4()),
            "document_id": document_id,
            "chunk_index": index,
            "heading": chunk.get("heading"),
            "content": content,
            "char_count": len(content),
            "estimated_tokens": int(chunk.get("estimated_tokens") or 0),
            "metadata": chunk.get("metadata") or {},
            "created_at": now,
        }
        records.append(record)

    existing_chunks = load_document_chunks()
    existing_chunks.extend(records)
    save_document_chunks(existing_chunks)

    return records


def list_document_chunks(document_id: str) -> list[dict[str, Any]]:
    chunks = load_document_chunks()
    document_chunks = [chunk for chunk in chunks if chunk["document_id"] == document_id]

    return sorted(
        document_chunks,
        key=lambda item: item.get("chunk_index", 0),
    )


def delete_document_chunks(document_id: str) -> None:
    chunks = load_document_chunks()
    next_chunks = [chunk for chunk in chunks if chunk["document_id"] != document_id]
    save_document_chunks(next_chunks)
