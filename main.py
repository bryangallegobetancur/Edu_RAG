import argparse
import os

from src.config import LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT, LANGCHAIN_ENDPOINT

if LANGCHAIN_TRACING_V2.lower() in ("true", "1") and LANGCHAIN_API_KEY:
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", LANGCHAIN_API_KEY)
    os.environ.setdefault("LANGCHAIN_PROJECT", LANGCHAIN_PROJECT)
    os.environ.setdefault("LANGCHAIN_ENDPOINT", LANGCHAIN_ENDPOINT)

from src.ingestion import ingest, load_vectorstore
from src.retrieval import ask, ask_with_sources


def cmd_ingest(args):
    ingest(args.docs_dir)


def cmd_query(args):
    vs = load_vectorstore()
    if args.sources:
        response = ask_with_sources(vs, args.question)
    else:
        response = ask(vs, args.question)
    print(f"\n{response}\n")


def main():
    parser = argparse.ArgumentParser(description="RAG Pipeline - LangChain + ChromaDB")
    sub = parser.add_subparsers(dest="command")

    ing = sub.add_parser("ingest", help="Indexar documentos en la base vectorial")
    ing.add_argument("docs_dir", help="Directorio con PDFs y TXTs")
    ing.set_defaults(func=cmd_ingest)

    q = sub.add_parser("query", help="Consultar la base de conocimiento")
    q.add_argument("question", help="Pregunta a responder")
    q.add_argument("--sources", "-s", action="store_true", help="Mostrar fuentes recuperadas")
    q.set_defaults(func=cmd_query)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
