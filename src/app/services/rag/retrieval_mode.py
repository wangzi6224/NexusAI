from typing import Literal, TypeAlias

RETRIEVAL_MODE_VECTOR_RERANK = "vector_rerank"
RETRIEVAL_MODE_HYBRID = "hybrid"

RetrievalMode: TypeAlias = Literal["vector_rerank", "hybrid"]
