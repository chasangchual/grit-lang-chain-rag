from embedding import Document
from embedding.loaders.file_loaders import TextFileLoader

def main():
    textFileLoader = TextFileLoader()
    documents: list[Document] = textFileLoader.load('/Users/sangcha/workspace/grit/grit-lang-chain-rag/README.MD')
    for document in documents:
        print(document)
if __name__ == "__main__":
    main()
