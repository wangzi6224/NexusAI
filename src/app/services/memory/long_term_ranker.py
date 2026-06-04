from __future__ import annotations

from datetime import datetime, timezone

from src.app.services.memory.long_term_schemas import LongTermMemoryItem


class LongTermMemoryRanker:
    def score(
        self,
        *,
        similarity_score: float,
        item: LongTermMemoryItem,
    ) -> float:
        """计算长期记忆项的综合评分。

        Args:
            similarity_score (float): 候选记忆与现有记忆的相似度评分。
            item (LongTermMemoryItem): 长期记忆项。

        Returns:
            float: 综合评分，范围在 0.0 到 1.0 之间。
        """
        recency = self._recency_score(item.updated_at)
        access = min(item.access_count / 10, 1.0)

        final_score = (
            similarity_score * 0.55
            + item.importance * 0.20
            + item.confidence * 0.15
            + recency * 0.07
            + access * 0.03
        )

        return max(0.0, min(final_score, 1.0))

    def _recency_score(self, updated_at: datetime | None) -> float:
        if updated_at is None:
            return 0.5

        now = datetime.now(timezone.utc)
        delta_days = max((now - updated_at).days, 0)

        if delta_days <= 7:
            return 1.0

        if delta_days <= 30:
            return 0.8

        if delta_days <= 90:
            return 0.5

        return 0.2
