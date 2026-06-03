from __future__ import annotations

import json
from typing import Any, cast

from src.app.db import get_connection
from src.app.services.memory.short_term_schemas import (
    ConversationState,
    ConversationStatePatch,
)


def _loads_jsonb(value: Any, default: Any) -> Any:
    """从数据库中检索出来的jsonb，可能是字符串（在某些数据库驱动中）或者已经被解析成Python对象了。"""
    if value is None:
        return default

    if isinstance(value, str):
        return json.loads(value)

    return value


def _row_to_state(row: dict[str, Any] | None) -> ConversationState | None:
    if row is None:
        return None

    data = dict(row)
    data["confirmed_facts"] = _loads_jsonb(data.get("confirmed_facts"), [])
    data["confirmed_constraints"] = _loads_jsonb(data.get("confirmed_constraints"), [])
    data["user_preferences"] = _loads_jsonb(data.get("user_preferences"), [])
    data["open_questions"] = _loads_jsonb(data.get("open_questions"), [])
    data["task_state"] = _loads_jsonb(data.get("task_state"), {})
    data["metadata"] = _loads_jsonb(data.get("metadata"), {})

    return ConversationState(**data)


class ShortTermMemoryStore:
    """会话级短期记忆仓储。

    职责边界：
    - 只负责 conversation_states 表的读写。
    - 不负责 messages。
    - 不负责 summary。
    - 不负责长期 memory_items。
    """

    def get_state(self, conversation_id: str) -> ConversationState | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM conversation_states
                    WHERE conversation_id = %(conversation_id)s
                    """,
                    {"conversation_id": conversation_id},
                )
                row = cur.fetchone()

        return _row_to_state(cast(dict[str, Any] | None, row))

    def upsert_state(
        self,
        conversation_id: str,
        patch: ConversationStatePatch,
    ) -> ConversationState:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversation_states (
                        conversation_id,
                        current_goal,
                        current_topic,
                        confirmed_facts,
                        confirmed_constraints,
                        user_preferences,
                        open_questions,
                        task_state,
                        source,
                        metadata,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %(conversation_id)s,
                        %(current_goal)s,
                        %(current_topic)s,
                        %(confirmed_facts)s::jsonb,
                        %(confirmed_constraints)s::jsonb,
                        %(user_preferences)s::jsonb,
                        %(open_questions)s::jsonb,
                        %(task_state)s::jsonb,
                        %(source)s,
                        %(metadata)s::jsonb,
                        NOW(),
                        NOW()
                    )
                    ON CONFLICT (conversation_id)
                    DO UPDATE SET
                        current_goal = COALESCE(EXCLUDED.current_goal, conversation_states.current_goal),
                        current_topic = COALESCE(EXCLUDED.current_topic, conversation_states.current_topic),
                        confirmed_facts = CASE
                            WHEN EXCLUDED.confirmed_facts = '[]'::jsonb THEN conversation_states.confirmed_facts
                            ELSE EXCLUDED.confirmed_facts
                        END,
                        confirmed_constraints = CASE
                            WHEN EXCLUDED.confirmed_constraints = '[]'::jsonb THEN conversation_states.confirmed_constraints
                            ELSE EXCLUDED.confirmed_constraints
                        END,
                        user_preferences = CASE
                            WHEN EXCLUDED.user_preferences = '[]'::jsonb THEN conversation_states.user_preferences
                            ELSE EXCLUDED.user_preferences
                        END,
                        open_questions = CASE
                            WHEN EXCLUDED.open_questions = '[]'::jsonb THEN conversation_states.open_questions
                            ELSE EXCLUDED.open_questions
                        END,
                        task_state = CASE
                            WHEN EXCLUDED.task_state = '{}'::jsonb THEN conversation_states.task_state
                            ELSE EXCLUDED.task_state
                        END,
                        source = EXCLUDED.source,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING *
                    """,
                    {
                        "conversation_id": conversation_id,
                        "current_goal": patch.current_goal,
                        "current_topic": patch.current_topic,
                        "confirmed_facts": json.dumps(
                            patch.confirmed_facts or [], ensure_ascii=False
                        ),
                        "confirmed_constraints": json.dumps(
                            patch.confirmed_constraints or [], ensure_ascii=False
                        ),
                        "user_preferences": json.dumps(
                            patch.user_preferences or [], ensure_ascii=False
                        ),
                        "open_questions": json.dumps(
                            patch.open_questions or [], ensure_ascii=False
                        ),
                        "task_state": json.dumps(
                            patch.task_state or {}, ensure_ascii=False
                        ),
                        "source": patch.source,
                        "metadata": json.dumps(
                            patch.metadata or {}, ensure_ascii=False
                        ),
                    },
                )
                row = cur.fetchone()

            conn.commit()

        state = _row_to_state(cast(dict[str, Any] | None, row))
        if state is None:
            raise RuntimeError("upsert conversation state failed")

        return state
