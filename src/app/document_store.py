import json
import uuid
from datetime import datetime
from typing import Any, cast

from psycopg import sql

from src.app.db import get_connection
from src.app.exceptions import AppError

ALLOWED_DOCUMENT_UPDATE_FIELDS = {
    "filename",
    "file_type",
    "source_path",
    "content",
    "status",
    "chunk_count",
    "char_count",
    "error_message",
}


def _row_to_dict(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None

    result = dict(row)

    for key in ["created_at", "updated_at"]:
        if isinstance(result.get(key), datetime):
            result[key] = result[key].isoformat()

    return result


def create_document(
    filename: str,
    file_type: str,
    source_path: str,
    content: str,
    status: str = "pending",
    error_message: str | None = None,
) -> dict[str, Any]:
    document_id = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (
                    id,
                    filename,
                    file_type,
                    source_path,
                    content,
                    status,
                    chunk_count,
                    char_count,
                    error_message,
                    created_at,
                    updated_at
                )
                VALUES (
                    %(id)s,
                    %(filename)s,
                    %(file_type)s,
                    %(source_path)s,
                    %(content)s,
                    %(status)s,
                    0,
                    %(char_count)s,
                    %(error_message)s,
                    NOW(),
                    NOW()
                )
                RETURNING *
                """,
                {
                    "id": document_id,
                    "filename": filename,
                    "file_type": file_type,
                    "source_path": source_path,
                    "content": content,
                    "status": status,
                    "char_count": len(content),
                    "error_message": error_message,
                },
            )
            row = cur.fetchone()

        conn.commit()

    document = _row_to_dict(dict(row) if row is not None else None)

    if document is None:
        raise AppError(
            code="DOCUMENT_STORE_ERROR",
            message="创建文档失败",
            status_code=500,
        )

    return document


def update_document(
    document_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    if not updates:
        updates = {}

    invalid_fields = set(updates) - ALLOWED_DOCUMENT_UPDATE_FIELDS
    if invalid_fields:
        raise AppError(
            code="DOCUMENT_STORE_ERROR",
            message="文档更新字段非法",
            detail=f"invalid_fields={sorted(invalid_fields)}",
            status_code=500,
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            if updates:
                set_sql = sql.SQL(", ").join(
                    sql.SQL("{} = {}").format(
                        sql.Identifier(key),
                        sql.Placeholder(key),
                    )
                    for key in updates
                )

                query = sql.SQL("""
                    UPDATE documents
                    SET {set_sql},
                        updated_at = NOW()
                    WHERE id = %(document_id)s
                    RETURNING *
                    """).format(set_sql=set_sql)

                params = {**updates, "document_id": document_id}
            else:
                query = sql.SQL("""
                    UPDATE documents
                    SET updated_at = NOW()
                    WHERE id = %(document_id)s
                    RETURNING *
                    """)
                params = {"document_id": document_id}

            cur.execute(query, params)
            row = cur.fetchone()

        conn.commit()

    document = _row_to_dict(dict(row) if row is not None else None)

    if document is None:
        raise AppError(
            code="DOCUMENT_NOT_FOUND",
            message="文档不存在",
            detail=f"document_id={document_id}",
            status_code=404,
        )

    return document


def get_document(document_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM documents
                WHERE id = %(document_id)s
                """,
                {"document_id": document_id},
            )
            row = cur.fetchone()

    return _row_to_dict(dict(row) if row is not None else None)


def list_documents() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM documents
                ORDER BY updated_at DESC
                """)
            rows = cur.fetchall()

    documents = [
        _row_to_dict(cast(dict[str, Any], row)) for row in rows if row is not None
    ]
    return [document for document in documents if document is not None]


def delete_document(document_id: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM documents
                WHERE id = %(document_id)s
                RETURNING id
                """,
                {"document_id": document_id},
            )
            row = cur.fetchone()

        conn.commit()

    if row is None:
        raise AppError(
            code="DOCUMENT_NOT_FOUND",
            message="文档不存在",
            detail=f"document_id={document_id}",
            status_code=404,
        )


def create_document_chunks(
    document_id: str,
    chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for index, chunk in enumerate(chunks):
                content = chunk.get("content", "").strip()
                if not content:
                    continue

                chunk_id = str(uuid.uuid4())

                cur.execute(
                    """
                    INSERT INTO document_chunks (
                        id,
                        document_id,
                        chunk_index,
                        heading,
                        content,
                        char_count,
                        estimated_tokens,
                        metadata,
                        embedding_status,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %(id)s,
                        %(document_id)s,
                        %(chunk_index)s,
                        %(heading)s,
                        %(content)s,
                        %(char_count)s,
                        %(estimated_tokens)s,
                        %(metadata)s::jsonb,
                        'pending',
                        NOW(),
                        NOW()
                    )
                    RETURNING *
                    """,
                    {
                        "id": chunk_id,
                        "document_id": document_id,
                        "chunk_index": index,
                        "heading": chunk.get("heading"),
                        "content": content,
                        "char_count": len(content),
                        "estimated_tokens": int(chunk.get("estimated_tokens") or 0),
                        "metadata": json.dumps(
                            chunk.get("metadata") or {},
                            ensure_ascii=False,
                        ),
                    },
                )

                row = cur.fetchone()
                if row is not None:
                    records.append(_chunk_row_to_dict(cast(dict[str, Any], row)))

        conn.commit()

    return records


def _chunk_row_to_dict(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)

    for key in ["created_at", "updated_at", "embedding_updated_at"]:
        if isinstance(result.get(key), datetime):
            result[key] = result[key].isoformat()

    if result.get("metadata") is None:
        result["metadata"] = {}

    return result


def list_document_chunks(document_id: str) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM document_chunks
                WHERE document_id = %(document_id)s
                ORDER BY chunk_index ASC
                """,
                {"document_id": document_id},
            )
            rows = cur.fetchall()

    return [_chunk_row_to_dict(cast(dict[str, Any], row)) for row in rows]


def delete_document_chunks(document_id: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM document_chunks
                WHERE document_id = %(document_id)s
                """,
                {"document_id": document_id},
            )

        conn.commit()
