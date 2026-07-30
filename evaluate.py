"""CLI de evaluación del RAG con LangSmith + LLM-as-a-Judge.

Comandos:
  gen-dataset : Genera un dataset golden sintético desde documentos y lo sube a LangSmith.
  run         : Ejecuta el RAG sobre el dataset y aplica los 6 jueces (correctness,
                groundedness, context_relevance, helpfulness, precision, recall).
                Sube el experimento a LangSmith.
  ab          : Comparación A/B de dos system prompts sobre el mismo dataset.

Requisitos previos:
  1. Tener `chroma_db/` creado (ejecuta antes `python main.py ingest <docs_dir>`).
  2. Tener el dataset en LangSmith (ejecuta antes `python evaluate.py gen-dataset ...`).

Ejemplo:
  python evaluate.py gen-dataset --docs-dir docs --n-questions 10
  python evaluate.py run --dataset RAG_eval_qa
  python evaluate.py ab --dataset RAG_eval_qa --prompt-a <file> --prompt-b <file>
"""
import argparse
import os
from typing import Optional

from src.config import (
    LANGCHAIN_API_KEY,
    LANGCHAIN_ENDPOINT,
    LANGCHAIN_PROJECT,
    LANGCHAIN_TRACING_V2,
    LANGSMITH_EVAL_DATASET,
    LANGSMITH_EVAL_EXPERIMENT,
    TOP_K,
)

if LANGCHAIN_TRACING_V2.lower() in ("true", "1") and LANGCHAIN_API_KEY:
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", LANGCHAIN_API_KEY)
    os.environ.setdefault("LANGCHAIN_PROJECT", LANGCHAIN_PROJECT)
    os.environ.setdefault("LANGCHAIN_ENDPOINT", LANGCHAIN_ENDPOINT)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langsmith import Client, evaluate

from src.dataset_gen import generate_dataset
from src.evaluators import ALL_EVALUATORS, judge_pair
from src.ingestion import load_vectorstore
from src.retrieval import build_rag_chain, format_docs, get_llm


# --- Cache del vectorstore (evita recargar embeddings en cada ejemplo) -------
_vs_cache = None


def _get_cached_vs():
    global _vs_cache
    if _vs_cache is None:
        _vs_cache = load_vectorstore()
    return _vs_cache


# --- Target para evaluate() -------------------------------------------------

def rag_target(inputs: dict) -> dict:
    """Target del RAG: devuelve {"answer", "contexts"} para que los jueces los consuman."""
    vs = _get_cached_vs()
    retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    docs = retriever.invoke(inputs["question"])
    contexts = [d.page_content for d in docs]
    chain = build_rag_chain(vs)
    answer = chain.invoke(inputs["question"])
    return {"answer": answer, "contexts": contexts}


def _build_chain_with_prompt(system_prompt: str):
    """Construye una cadena RAG con un system prompt personalizado (para A/B)."""
    vs = _get_cached_vs()
    retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    llm = get_llm()
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    ), vs, retriever


# --- Comandos ---------------------------------------------------------------

def cmd_gen_dataset(args):
    n = generate_dataset(args.docs_dir, args.n_questions, args.dataset_name)
    print(f"\nListo. {n} ejemplos subidos a LangSmith.")


def cmd_run(args):
    dataset_name = args.dataset or LANGSMITH_EVAL_DATASET
    experiment = args.experiment or LANGSMITH_EVAL_EXPERIMENT
    threshold_val = args.threshold
    print(f"Ejecutando evaluación sobre dataset '{dataset_name}'...")
    results = evaluate(
        rag_target,
        data=dataset_name,
        evaluators=ALL_EVALUATORS,
        experiment_prefix=experiment,
        max_concurrency=args.concurrency,
    )
    print("\n=== Resultados del experimento ===")
    try:
        df = results.to_pandas()
        metric_cols = ["correctness", "groundedness", "context_relevance", "helpfulness", "precision", "recall", "faithfulness"]
        existing = [c for c in metric_cols if c in df.columns]
        print(df[existing].describe())
        print(f"\n{'='*60}")
        print(f"THRESHOLD ANALYSIS (threshold={threshold_val})")
        print(f"{'='*60}")
        for col in existing:
            passed = (df[col] >= threshold_val).sum()
            total = df[col].notna().sum()
            mean = df[col].mean()
            print(f"  {col:25s}  mean={mean:.3f}  pass_rate={passed}/{total} ({100*passed/total:.1f}%)")
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        print(results)


def cmd_ab(args):
    """Comparación A/B de dos system prompts sobre el dataset."""
    with open(args.prompt_a, encoding="utf-8") as f:
        prompt_a = f.read()
    with open(args.prompt_b, encoding="utf-8") as f:
        prompt_b = f.read()

    client = Client()
    examples = list(client.list_examples(dataset_name=args.dataset or LANGSMITH_EVAL_DATASET))
    if not examples:
        raise RuntimeError(f"Dataset '{args.dataset or LANGSMITH_EVAL_DATASET}' vacío o inexistente.")

    chain_a, vs_a, ret_a = _build_chain_with_prompt(prompt_a)
    chain_b, vs_b, ret_b = _build_chain_with_prompt(prompt_b)

    print(f"Comparando A vs B sobre {len(examples)} ejemplos...\n")
    wins_a = wins_b = ties = 0
    sum_a = sum_b = 0.0
    for i, ex in enumerate(examples, 1):
        question = ex.inputs["question"]
        reference = ex.outputs.get("answer", "")
        docs = ret_a.invoke(question)
        context = format_docs(docs)
        ans_a = chain_a.invoke({"context": context, "question": question})
        ans_b = chain_b.invoke({"context": context, "question": question})
        verdict = judge_pair(question, ans_a, ans_b, reference=reference)
        sum_a += verdict["score_a"]
        sum_b += verdict["score_b"]
        if verdict["winner"] == "A":
            wins_a += 1
        elif verdict["winner"] == "B":
            wins_b += 1
        else:
            ties += 1
        print(f"[{i}] winner={verdict['winner']}  A={verdict['score_a']:.2f}  B={verdict['score_b']:.2f}")
        print(f"    {verdict['reason'][:150]}")

    n = len(examples)
    print("\n=== Resumen A/B ===")
    print(f"Victorias A: {wins_a}  |  B: {wins_b}  |  Empates: {ties}")
    print(f"Score medio A: {sum_a/n:.3f}  |  B: {sum_b/n:.3f}")
    print(f"Ganador global: {'A' if sum_a > sum_b else 'B' if sum_b > sum_a else 'empate'}")


def main():
    parser = argparse.ArgumentParser(description="Evaluación del RAG con LangSmith + LLM-as-a-Judge")
    sub = parser.add_subparsers(dest="command")

    g = sub.add_parser("gen-dataset", help="Generar dataset golden sintético en LangSmith")
    g.add_argument("--docs-dir", required=True, help="Directorio con PDFs/TXTs")
    g.add_argument("--n-questions", type=int, default=10)
    g.add_argument("--dataset-name", default=None)
    g.set_defaults(func=cmd_gen_dataset)

    r = sub.add_parser("run", help="Ejecutar evaluación sobre el dataset")
    r.add_argument("--dataset", default=None, help="Nombre del dataset en LangSmith")
    r.add_argument("--experiment", default=None, help="Prefijo del experimento")
    r.add_argument("--concurrency", type=int, default=2)
    r.add_argument("--threshold", type=float, default=0.7, help="Umbral mínimo para pasar cada métrica (defecto: 0.7)")
    r.set_defaults(func=cmd_run)

    a = sub.add_parser("ab", help="Comparación A/B de dos system prompts")
    a.add_argument("--dataset", default=None)
    a.add_argument("--prompt-a", required=True, help="Archivo con system prompt A")
    a.add_argument("--prompt-b", required=True, help="Archivo con system prompt B")
    a.set_defaults(func=cmd_ab)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
