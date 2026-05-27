from typing import Any

from src.app.db import get_connection


class PgKeywordStore:
    def search_keyword_chunks(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH q AS (
                        SELECT websearch_to_tsquery('simple', %(query)s) AS query
                    )
                    SELECT
                        dc.id AS chunk_id,
                        dc.document_id,
                        d.filename,
                        dc.chunk_index,
                        dc.heading,
                        dc.content,
                        dc.metadata,
                        ts_rank_cd(dc.search_vector, q.query, 32) AS keyword_score
                    FROM document_chunks dc
                    JOIN documents d ON d.id = dc.document_id
                    CROSS JOIN q
                    WHERE dc.search_vector @@ q.query
                    ORDER BY keyword_score DESC
                    LIMIT %(top_k)s
                    """,
                    {
                        "query": query,
                        "top_k": top_k,
                    },
                )
                return [dict(row) for row in cur.fetchall()]
