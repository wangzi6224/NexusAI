import uuid
from datetime import datetime
from typing import Any

from src.app.db import get_connection


def _normalize_history_row(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)

    if isinstance(result.get("timestamp"), datetime):
        result["timestamp"] = result["timestamp"].isoformat()

    return {
        "timestamp": result["timestamp"],
        "model": result["model"],
        "user_input": result["user_input"],
        "prompt": result["prompt"],
        "answer": result["answer"],
        "elapsed_seconds": float(result["elapsed_seconds"]),
    }


def load_history() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    timestamp,
                    model,
                    user_input,
                    prompt,
                    answer,
                    elapsed_seconds
                FROM chat_history
                ORDER BY created_at ASC
                """)
            rows = cur.fetchall()

    return [_normalize_history_row(row) for row in rows]


def append_history(record: dict[str, Any]) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_history (
                    id,
                    timestamp,
                    model,
                    user_input,
                    prompt,
                    answer,
                    elapsed_seconds,
                    created_at
                )
                VALUES (
                    %(id)s,
                    %(timestamp)s,
                    %(model)s,
                    %(user_input)s,
                    %(prompt)s,
                    %(answer)s,
                    %(elapsed_seconds)s,
                    NOW()
                )
                """,
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": record.get("timestamp") or datetime.now(),
                    "model": record["model"],
                    "user_input": record["user_input"],
                    "prompt": record["prompt"],
                    "answer": record["answer"],
                    "elapsed_seconds": record["elapsed_seconds"],
                },
            )

        conn.commit()


def clear_history() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chat_history")

        conn.commit()
