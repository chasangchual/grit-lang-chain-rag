from .base import DocumentLoader, LoaderDependencyError, LoaderRegistry
from .file_loaders import ExcelLoader, FileSystemLoader, PdfLoader, PowerPointLoader, TextFileLoader, WordLoader
from .url_loader import WebUrlLoader


def build_default_registry(text_encoding: str = "utf-8") -> LoaderRegistry:
    registry = LoaderRegistry()
    registry.register(WebUrlLoader())
    registry.register(TextFileLoader(encoding=text_encoding))
    registry.register(PdfLoader())
    registry.register(WordLoader())
    registry.register(ExcelLoader())
    registry.register(PowerPointLoader())
    return registry


__all__ = [
    "DocumentLoader",
    "LoaderDependencyError",
    "LoaderRegistry",
    "FileSystemLoader",
    "TextFileLoader",
    "PdfLoader",
    "WordLoader",
    "ExcelLoader",
    "PowerPointLoader",
    "WebUrlLoader",
    "build_default_registry",
]
