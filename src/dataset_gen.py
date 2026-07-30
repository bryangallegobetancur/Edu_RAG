"""Generación de dataset golden sintético para evaluación en LangSmith.

Lee documentos de un directorio, los trocea, y pide al LLM juez que genere
pares pregunta/respuesta (con respuesta anotada en el propio documento). Luego
sube el dataset a LangSmith para usarlo con `evaluate(...)`.

Uso:
    python -m src.dataset_gen --docs-dir docs --n-questions 10
    python evaluate.py gen-dataset --docs-dir docs --n-questions 10
"""
import argparse
import json
import re
from typing import List

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import Client

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    LANGSMITH_EVAL_DATASET,
)
from src.evaluators import get_judge_llm
from src.ingestion import load_documents


def _split(docs, max_chunks: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    texts = [c.page_content for c in chunks if c.page_content.strip()]
    return texts[:max_chunks]


def _generate_qa_from_chunk(chunk: str) -> List[dict]:
    """Pide al juez que genere 1-3 pares Q/A a partir de un fragmento de texto."""
    llm = get_judge_llm()
    system = (
        "Eres un generador de datasets de evaluación para un RAG. A partir del "
        "TEXTO proporcionado, genera de 1 a 3 pares pregunta/respuesta que un "
        "usuario real haría y que se puedan responder USANDO SOLO ese texto. "
        "La respuesta debe ser fiel al texto, en español, y contener la "
        "información clave. Devuelve SOLO un JSON: "
        '{"items": [{"question": "...", "answer": "..."}, ...]}.'
    )
    user = f"TEXTO:\n{chunk}\n\nDevuelve el JSON."
    raw = llm.invoke([SystemMessage(system), HumanMessage(user)])
    match = re.search(r"\{.*\}", raw.content, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    items = data.get("items", [])
    return [it for it in items if it.get("question") and it.get("answer")]


def generate_dataset(docs_dir: str, n_questions: int = 10, dataset_name: str = None) -> int:
    """Genera Q/A desde docs_dir y sube el dataset a LangSmith.

    Devuelve el número de ejemplos subidos.
    """
    dataset_name = dataset_name or LANGSMITH_EVAL_DATASET
    print(f"Cargando documentos desde: {docs_dir}")
    docs = load_documents(docs_dir)
    if not docs:
        raise RuntimeError(f"No se encontraron documentos en {docs_dir}")
    print(f"Documentos cargados: {len(docs)}")

    # Heurística: procesar ~3x chunks de los que queremos preguntas
    max_chunks = max(3, n_questions * 3)
    texts = _split(docs, max_chunks=max_chunks)
    print(f"Fragmentos a procesar: {len(texts)} (objetivo: {n_questions} preguntas)")

    examples = []
    for i, chunk in enumerate(texts, 1):
        if len(examples) >= n_questions:
            break
        print(f"  [{i}/{len(texts)}] generando Q/A...")
        try:
            qa = _generate_qa_from_chunk(chunk)
        except Exception as e:
            print(f"    error: {e}")
            continue
        for it in qa:
            if len(examples) >= n_questions:
                break
            examples.append({
                "inputs": {"question": it["question"].strip()},
                "outputs": {"answer": it["answer"].strip()},
            })
        print(f"    acumulado: {len(examples)}/{n_questions}")

    if not examples:
        raise RuntimeError("No se generaron ejemplos. Revisa el texto o el juez.")

    client = Client()
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Dataset Q/A sintético generado automáticamente para evaluación del RAG.",
    )
    for ex in examples:
        client.create_example(
            inputs=ex["inputs"],
            outputs=ex["outputs"],
            dataset_id=dataset.id,
        )
    print(f"\nDataset '{dataset_name}' creado en LangSmith con {len(examples)} ejemplos.")
    print(f"URL: https://smith.langchain.com/o/default/datasets/{dataset.id}")
    return len(examples)


def main():
    parser = argparse.ArgumentParser(description="Generar dataset golden sintético en LangSmith")
    parser.add_argument("--docs-dir", required=True, help="Directorio con PDFs/TXTs")
    parser.add_argument("--n-questions", type=int, default=10, help="Nº de pares Q/A a generar")
    parser.add_argument("--dataset-name", default=None, help="Nombre del dataset en LangSmith")
    args = parser.parse_args()
    generate_dataset(args.docs_dir, args.n_questions, args.dataset_name)


if __name__ == "__main__":
    main()
