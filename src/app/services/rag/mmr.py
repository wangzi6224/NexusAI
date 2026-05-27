from difflib import SequenceMatcher
from typing import Any


def content_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a[:800], b[:800]).ratio()


def select_mmr(
    chunks: list[dict[str, Any]],
    top_k: int = 10,
    lambda_mult: float = 0.7,
    duplicate_threshold: float = 0.85,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    candidates = chunks[:]

    while candidates and len(selected) < top_k:
        best_item: dict[str, Any] | None = None
        best_score = float("-inf")

        for item in candidates:
            relevance = float(item.get("rrf_score") or 0)

            if not selected:
                diversity_penalty = 0.0
            else:
                diversity_penalty = max(
                    content_similarity(item["content"], selected_item["content"])
                    for selected_item in selected
                )

            # 过于重复的 chunk 直接跳过
            if diversity_penalty >= duplicate_threshold:
                continue

            mmr_score = lambda_mult * relevance - (1 - lambda_mult) * diversity_penalty

            if mmr_score > best_score:
                best_score = mmr_score
                best_item = item

        if best_item is None:
            break

        best_item["mmr_score"] = round(float(best_score), 6)
        best_item["mmr_selected"] = True
        selected.append(best_item)
        candidates.remove(best_item)

    for index, item in enumerate(selected):
        item["mmr_rank"] = index + 1

    return selected
