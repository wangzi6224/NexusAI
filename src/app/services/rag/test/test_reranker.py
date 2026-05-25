from src.app.services.rag.rag_service import RagService
from src.app.services.rag.reranker import RagReranker


# 这个测试函数主要是为了验证 RagReranker 的基本功能是否正常。
def test_reranker():
    rag_service = RagService()
    reranker = RagReranker()

    question = "什么是 RAG？"
    search_result = rag_service.search(query=question, top_k=3)

    chunks = search_result["chunks"]

    rerank_result = reranker.rerank(
        query=question,
        chunks=chunks,
        top_n=3,
    )

    print("Search Result:")
    for i, chunk in enumerate(chunks):
        print(f"{i+1}. {chunk['content']} (score: {chunk.get('score')})")

    print("\nRerank Result:")
    for i, chunk in enumerate(rerank_result["chunks"]):
        print(f"{i+1}. {chunk['content']} (rerank_score: {chunk.get('rerank_score')})")


# test_reranker()
