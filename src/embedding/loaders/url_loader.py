from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from langchain_community.document_loaders import WebBaseLoader

from .base import DocumentLoader, build_document
from ..models import Document


class WebUrlLoader(DocumentLoader):
    def supports(self, source: str | Path) -> bool:
        if isinstance(source, Path):
            return False
        parsed = urlparse(source)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def load(self, source: str | Path) -> list[Document]:
        url = str(source)
        docs = WebBaseLoader(web_paths=[url]).load()
        return [
            build_document(
                url,
                "url",
                doc.page_content,
                {"title": doc.metadata.get("title"), "language": doc.metadata.get("language")},
            )
            for doc in docs
            if doc.page_content
        ]
