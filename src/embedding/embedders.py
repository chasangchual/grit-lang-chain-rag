from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib

from langchain_ollama import OllamaEmbeddings

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "nomic-embed-text", base_url: str | None = None) -> None:
        kwargs = {"model": model}
        if base_url:
            kwargs["base_url"] = base_url
        self._embedder = OllamaEmbeddings(**kwargs)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._embedder.embed_documents(texts)
        return [list(vector) for vector in vectors]


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic lightweight embedding useful for local testing."""

    def __init__(self, dimensions: int = 128) -> None:
        self._dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            repeats = (self._dimensions + len(digest) - 1) // len(digest)
            expanded = (digest * repeats)[: self._dimensions]
            vectors.append([byte / 255.0 for byte in expanded])
        return vectors
