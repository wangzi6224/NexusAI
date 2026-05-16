from pathlib import Path

from src.app.services.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)

provider = SentenceTransformerEmbeddingProvider()

docs: Path = Path("docs") / "text.txt"

content = docs.read_text(encoding="utf-8")

vector = provider.embed_text(content)

print("嵌入模型模型:", provider.model_name)
print("纬度:", provider.dimension())
print("向量长度:", len(vector))
print("预览:", vector[:5])
