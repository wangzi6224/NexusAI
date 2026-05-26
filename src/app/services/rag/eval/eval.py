import json
from pathlib import Path

from src.app.services.rag.retriever import RagRetriever


def load_eval_questions() -> list[dict]:
    path = Path(__file__).parent / "eval_questions.json"
    return json.loads(path.read_text(encoding="utf-8"))


def contains_expected_keyword(
    chunks: list[dict],
    expected_keywords: list[str],
) -> bool:
    merged_content = "\n".join(str(chunk.get("content", "")) for chunk in chunks)

    return any(keyword in merged_content for keyword in expected_keywords)


def run_eval(rerank_enabled: bool) -> dict:
    retriever = RagRetriever()
    questions = load_eval_questions()

    total = len(questions)
    hit_count = 0
    details = []

    for item in questions:
        result = retriever.search(
            query=item["query"],
            top_k=5,
            candidate_k=30,
            rerank_top_n=5,
            score_threshold=0.25,
            rerank_enabled=rerank_enabled,
        )

        hit = contains_expected_keyword(
            chunks=result["chunks"],
            expected_keywords=item["expected_keywords"],
        )

        if hit:
            hit_count += 1

        details.append(
            {
                "id": item["id"],
                "query": item["query"],
                "hit": hit,
                "candidate_count": result["trace"]["candidate_count"],
                "rerank_enabled": result["trace"]["rerank_enabled"],
                "rerank_latency_ms": result["trace"]["rerank_latency_ms"],
            }
        )

    return {
        "rerank_enabled": rerank_enabled,
        "total": total,
        "hit_count": hit_count,
        "hit_rate": round(hit_count / total, 4) if total else 0,
        "details": details,
    }


if __name__ == "__main__":
    print("Without Rerank:")
    print(json.dumps(run_eval(False), ensure_ascii=False, indent=2))

    print("With Rerank:")
    print(json.dumps(run_eval(True), ensure_ascii=False, indent=2))
