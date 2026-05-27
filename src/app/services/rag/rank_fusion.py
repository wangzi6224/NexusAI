from typing import Any, Literal


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict[str, Any]]],
    top_k: int = 20,
    k: int = 60,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}

    for source_index, chunks in enumerate(ranked_lists):
        source_name: Literal["vector"] | Literal["keyword"] = (
            "vector" if source_index == 0 else "keyword"
        )

        for rank, chunk in enumerate(chunks, start=1):
            chunk_id = chunk["chunk_id"]

            if chunk_id not in merged:
                merged[chunk_id] = {
                    **chunk,
                    "rrf_score": 0.0,
                    "matched_sources": [],
                    "vector_rank": None,
                    "keyword_rank": None,
                    "vector_score": None,
                    "keyword_score": None,
                }

            merged_item = merged[chunk_id]
            merged_item["rrf_score"] += 1 / (k + rank)

            if source_name not in merged_item["matched_sources"]:
                merged_item["matched_sources"].append(source_name)

            if source_name == "vector":
                merged_item["vector_rank"] = rank
                merged_item["vector_score"] = chunk.get("score")
                merged_item["vector_distance"] = chunk.get("distance")

            if source_name == "keyword":
                merged_item["keyword_rank"] = rank
                merged_item["keyword_score"] = chunk.get("keyword_score")

    result = list(merged.values())

    result.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    for index, item in enumerate(result):
        item["fusion_rank"] = index + 1
        item["rrf_score"] = round(float(item["rrf_score"]), 6)

    return result[:top_k]
