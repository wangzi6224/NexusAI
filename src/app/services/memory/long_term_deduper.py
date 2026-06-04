from __future__ import annotations

from src.app.services.memory.long_term_schemas import (
    LongTermMemoryCreate,
    LongTermMemoryItem,
)
from src.app.services.memory.long_term_store import (
    LongTermMemoryStore,
    normalize_memory_content,
)


class LongTermMemoryDeduper:
    """长期记忆去重器。

    负责比较候选记忆与现有长期记忆，避免重复内容被多次保存。
    """

    def __init__(self, store: LongTermMemoryStore) -> None:
        self.store = store

    def find_duplicate(
        self,
        payload: LongTermMemoryCreate,
    ) -> LongTermMemoryItem | None:
        """查找与候选记忆重复或高度相似的已有记忆。

        返回第一个完全匹配的记忆；如果没有完全匹配，则返回最相似的一条；
        如果没有候选相似记忆，则返回 None。
        """
        normalized = normalize_memory_content(payload.content)

        similar = self.store.find_similar_by_text(
            user_id=payload.user_id,
            normalized_content=normalized,
            memory_type=payload.memory_type,
            limit=3,
        )

        if not similar:
            return None

        for item in similar:
            if item.normalized_content == normalized:
                return item

        return similar[0]
