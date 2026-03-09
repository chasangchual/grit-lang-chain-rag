from __future__ import annotations

from .config import PipelineConfig
from .embedders import EmbeddingProvider, OllamaEmbeddingProvider
from .loaders import build_default_registry
from .pipeline import EmbeddingPipeline
from .splitters import RecursiveTextSplitter


def build_default_pipeline(
    config: PipelineConfig | None = None,
    embedder: EmbeddingProvider | None = None,
) -> EmbeddingPipeline:
    cfg = config or PipelineConfig()
    return EmbeddingPipeline(
        registry=build_default_registry(text_encoding=cfg.text_encoding),
        splitter=RecursiveTextSplitter(chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap),
        embedder=embedder or OllamaEmbeddingProvider(),
        config=cfg,
    )
