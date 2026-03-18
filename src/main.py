from pathlib import Path
from typing import List

from embedding import Document
from embedding.loaders.file_loaders import LoaderRegistry
import pprint as pp
from embedding.splitters import DocumentSplitter,RecursiveTextSplitter
from embedding.pipeline import EmbeddingPipeline, EmbeddedChunk, EmbeddingProvider
from embedding.embedders import OllamaEmbeddingProvider
from embedding.loaders import build_default_registry

def main():
    # loader: FileSystemLoader = FileSystemLoader(path="/Users/sangcha/Documents/Shakudo/ICI", recursive=False)
    # docSpliter: DocumentSplitter = RecursiveTextSplitter()
    # documents: list[Document] = loader.load()
    # for doc in documents:
    #     chunks: List[str] = docSpliter.split(doc)
    #     for chunk in chunks:
    #         pp.pprint(chunk)
    splitter: DocumentSplitter = RecursiveTextSplitter() 
    embedder: EmbeddingProvider = OllamaEmbeddingProvider() 
        
    pipeline = EmbeddingPipeline(registry=build_default_registry(), splitter=splitter, embedder=embedder)
    
    embendings : List[EmbeddedChunk] = pipeline.process_directory(Path("/Users/sangcha/Documents/Shakudo/ICI"));
    for embending in embendings:
        pp.pprint(embending)
                
if __name__ == "__main__":
    main()
