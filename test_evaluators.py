"""Test rápido de los evaluadores LLM-as-judge con un Run/Example simulados."""
import uuid
from datetime import datetime, timezone
from langsmith.schemas import Run, Example
from src.evaluators import correctness, groundedness, context_relevance, helpfulness, precision, recall, faithfulness, threshold, judge_pair

now = datetime.now(timezone.utc)
rid = uuid.uuid4()

# Run simulado: respuesta del RAG + contextos recuperados
run = Run(
    id=str(rid),
    trace_id=str(rid),
    name="rag",
    run_type="chain",
    start_time=now,
    inputs={"question": "¿Cuántos días tengo para devolver un producto?"},
    outputs={
        "answer": "Tienes 30 días desde la fecha de compra para devolver un producto.",
        "contexts": [
            "La tienda Acme acepta devoluciones de productos dentro de los 30 días siguientes a la fecha de compra."
        ],
    },
)

# Example simulado: respuesta golden
example = Example(
    id=str(uuid.uuid4()),
    inputs={"question": "¿Cuántos días tengo para devolver un producto?"},
    outputs={"answer": "El plazo de devolución es de 30 días desde la compra."},
)

print("=== correctness ===")
print(correctness(run, example))
print("\n=== groundedness ===")
print(groundedness(run, example))
print("\n=== context_relevance ===")
print(context_relevance(run, example))
print("\n=== helpfulness ===")
print(helpfulness(run, example))

print("\n=== precision ===")
print(precision(run, example))
print("\n=== recall ===")
print(recall(run, example))
print("\n=== faithfulness ===")
print(faithfulness(run, example))

# Run simulado para threshold (inyecta puntuaciones en run.outputs)
run_threshold = Run(
    id=str(uuid.uuid4()),
    trace_id=str(uuid.uuid4()),
    name="rag_threshold",
    run_type="chain",
    start_time=now,
    inputs={"question": "¿Cuántos días tengo para devolver un producto?"},
    outputs={
        "answer": "Tienes 30 días.",
        "correctness": 0.9,
        "groundedness": 0.85,
        "context_relevance": 0.75,
        "helpfulness": 0.95,
        "precision": 0.8,
        "recall": 0.6,
        "faithfulness": 0.88,
        "_threshold": 0.7,
    },
)
print("\n=== threshold (0.7 - esperado 1.0) ===")
print(threshold(run_threshold, example))

run_threshold_fail = Run(
    id=str(uuid.uuid4()),
    trace_id=str(uuid.uuid4()),
    name="rag_threshold_fail",
    run_type="chain",
    start_time=now,
    inputs={"question": "¿Cuántos días tengo para devolver un producto?"},
    outputs={
        "answer": "Tienes 30 días.",
        "correctness": 0.9,
        "groundedness": 0.85,
        "context_relevance": 0.75,
        "helpfulness": 0.95,
        "precision": 0.8,
        "recall": 0.6,
        "faithfulness": 0.88,
        "_threshold": 0.9,
    },
)
print("\n=== threshold (0.9 - esperado 0.0) ===")
print(threshold(run_threshold_fail, example))

print("\n=== judge_pair (A/B) ===")
verdict = judge_pair(
    question="¿Cuántos días tengo para devolver un producto?",
    answer_a="Tienes 30 días desde la fecha de compra.",
    answer_b="No lo sé.",
    reference="El plazo de devolución es de 30 días desde la compra.",
)
print(verdict)
