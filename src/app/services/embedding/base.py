from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]: ...

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def dimension(self) -> int: ...
