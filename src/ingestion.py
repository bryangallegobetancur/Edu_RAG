from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import (
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_documents(docs_dir: str):
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    pdf_docs = loader.load()

    txt_loader = DirectoryLoader(
        docs_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )
    txt_docs = txt_loader.load()

    return pdf_docs + txt_docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest(docs_dir: str):
    print(f"Loading documents from: {docs_dir}")
    docs = load_documents(docs_dir)
    print(f"Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    embeddings = get_embeddings()
    print(f"Using embedding model: {EMBEDDING_MODEL}")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"Vector store saved to: {CHROMA_PERSIST_DIR}")
    return vectorstore


def ingest_pdf(file_path: str, vectorstore=None):
    """Indexa un único PDF en el vector store existente.

    Si no se pasa un vectorstore, carga el persistido en CHROMA_PERSIST_DIR.
    Devuelve la cantidad de chunks añadidos.
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    chunks = chunk_documents(docs)

    if vectorstore is None:
        vectorstore = load_vectorstore()

    vectorstore.add_documents(chunks)
    return len(chunks)


def load_vectorstore():
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.ingestion <docs_directory>")
        sys.exit(1)

    ingest(sys.argv[1])
