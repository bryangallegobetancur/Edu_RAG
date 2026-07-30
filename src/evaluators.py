"""Evaluadores LLM-as-a-Judge para el RAG.

Cada evaluador es una función `(run, example) -> dict` compatible con
`langsmith.evaluate(...)`. Devuelve `{"key", "score", "comment"}`.

Métricas implementadas:
  - correctness        : fidelidad vs. respuesta de referencia (golden).
  - groundedness       : la respuesta está respaldada por el contexto recuperado.
  - context_relevance  : los documentos recuperados son útiles para la pregunta.
  - helpfulness        : la respuesta es útil, clara y concisa.
  - precision          : fracción de docs recuperados que son relevantes (|R ∩ Rec| / |Rec|).
  - recall             : cobertura de los docs recuperados vs. info necesaria (|R ∩ Rec| / |R|).

El juez es `qwen3.7-plus` vía OpenCode Go (configurable en .env).
"""
import json
import re
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config import (
    JUDGE_MODEL,
    JUDGE_TEMPERATURE,
    OPENCODE_GO_API_KEY,
    OPENCODE_GO_BASE_URL,
)


def get_judge_llm() -> ChatOpenAI:
    """Devuelve el LLM que actúa como juez (qwen3.7-plus vía OpenCode Go)."""
    return ChatOpenAI(
        model=JUDGE_MODEL,
        api_key=OPENCODE_GO_API_KEY,
        base_url=OPENCODE_GO_BASE_URL,
        temperature=JUDGE_TEMPERATURE,
    )


def _extract_json(text: str) -> dict:
    """Extrae el primer objeto JSON válido de la respuesta del juez."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        try:
            return json.loads(match.group(0).replace("'", '"'))
        except json.JSONDecodeError:
            return {}


def _clamp01(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


def _judge(system: str, user: str, key: str) -> dict:
    """Ejecuta el juez y devuelve el resultado en formato LangSmith."""
    llm = get_judge_llm()
    raw = llm.invoke([SystemMessage(system), HumanMessage(user)])
    parsed = _extract_json(raw.content)
    score = _clamp01(parsed.get("score"))
    comment = parsed.get("reason") or parsed.get("comment") or raw.content[:300]
    return {"key": key, "score": score, "comment": comment}


def _get(run_output: dict, *keys: str, default: Any = "") -> Any:
    for k in keys:
        if k in run_output:
            return run_output[k]
    return default


def correctness(run, example) -> dict:
    """Compara la respuesta del RAG contra la respuesta de referencia (golden)."""
    prediction = _get(run.outputs, "answer", "response", "output")
    reference = ""
    if example is not None and example.outputs:
        reference = _get(example.outputs, "answer", "response", "output")
    question = ""
    if example is not None and example.inputs:
        question = _get(example.inputs, "question", "query", "input")

    system = (
        "Eres un evaluador experto. Compara la respuesta del candidato con la "
        "respuesta de referencia para la misma pregunta. Puntúa la CORRECTITUD "
        "de 0.0 a 1.0, donde 1.0 = equivalente en información clave y 0.0 = "
        "totalmente incorrecta. Devuelve SOLO JSON: "
        '{"score": <float>, "reason": "<breve justificación en español>"}.'
    )
    user = (
        f"Pregunta:\n{question}\n\n"
        f"Respuesta de referencia:\n{reference}\n\n"
        f"Respuesta del candidato:\n{prediction}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "correctness")


def groundedness(run, example) -> dict:
    """Verifica que la respuesta esté respaldada por el contexto recuperado (no alucinación)."""
    prediction = _get(run.outputs, "answer", "response", "output")
    contexts = _get(run.outputs, "contexts", "context", "documents", default=[])
    if isinstance(contexts, list):
        context_text = "\n\n".join(str(c) for c in contexts)
    else:
        context_text = str(contexts)

    system = (
        "Eres un evaluador experto en detección de alucinaciones. Dado un "
        "CONTEXTO recuperado y una RESPUESTA, decide si TODAS las afirmaciones "
        "fácticas de la respuesta están respaldadas por el contexto. Puntúa la "
        "FUNDAMENTACIÓN de 0.0 a 1.0, donde 1.0 = totalmente respaldada y 0.0 = "
        "alucinada/inventada. Penaliza afirmaciones no presentes en el contexto. "
        'Devuelve SOLO JSON: {"score": <float>, "reason": "<breve en español>"}.'
    )
    user = (
        f"CONTEXTO recuperado:\n{context_text}\n\n"
        f"RESPUESTA a evaluar:\n{prediction}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "groundedness")


def context_relevance(run, example) -> dict:
    """Evalúa si los documentos recuperados son relevantes para la pregunta."""
    contexts = _get(run.outputs, "contexts", "context", "documents", default=[])
    if isinstance(contexts, list):
        context_text = "\n\n".join(str(c) for c in contexts)
    else:
        context_text = str(contexts)
    question = ""
    if example is not None and example.inputs:
        question = _get(example.inputs, "question", "query", "input")
    elif run.inputs:
        question = _get(run.inputs, "question", "query", "input")

    system = (
        "Eres un evaluador experto en sistemas RAG. Dado una PREGUNTA y los "
        "DOCUMENTOS recuperados, decide si estos documentos contienen información "
        "ÚTIL para responder la pregunta. Puntúa la RELEVANCIA del contexto de "
        "0.0 a 1.0, donde 1.0 = muy relevante y 0.0 = totalmente irrelevante. "
        'Devuelve SOLO JSON: {"score": <float>, "reason": "<breve en español>"}.'
    )
    user = (
        f"PREGUNTA:\n{question}\n\n"
        f"DOCUMENTOS recuperados:\n{context_text}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "context_relevance")


def helpfulness(run, example) -> dict:
    """Evalúa si la respuesta es útil, clara y concisa para el usuario."""
    prediction = _get(run.outputs, "answer", "response", "output")
    question = ""
    if example is not None and example.inputs:
        question = _get(example.inputs, "question", "query", "input")
    elif run.inputs:
        question = _get(run.inputs, "question", "query", "input")

    system = (
        "Eres un evaluador experto en experiencia de usuario de chatbots. Dado "
        "una PREGUNTA y la RESPUESTA, evalúa si es ÚTIL, CLARA y CONCISA para el "
        "usuario. Puntúa de 0.0 a 1.0, donde 1.0 = excelente y 0.0 = inútil. "
        "Penaliza respuestas vagas, excesivamente largas o que ignoran la pregunta. "
        'Devuelve SOLO JSON: {"score": <float>, "reason": "<breve en español>"}.'
    )
    user = (
        f"PREGUNTA:\n{question}\n\n"
        f"RESPUESTA:\n{prediction}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "helpfulness")


def precision(run, example) -> dict:
    """Evalúa qué fracción de los documentos recuperados son relevantes para la pregunta.

    Precisión = documentos relevantes recuperados / total documentos recuperados.
    El juez puntúa de 0.0 (ninguno relevante) a 1.0 (todos relevantes).
    """
    contexts = _get(run.outputs, "contexts", "context", "documents", default=[])
    if isinstance(contexts, list):
        context_text = "\n\n".join(str(c) for c in contexts)
    else:
        context_text = str(contexts)

    question = ""
    if example is not None and example.inputs:
        question = _get(example.inputs, "question", "query", "input")
    elif run.inputs:
        question = _get(run.inputs, "question", "query", "input")

    system = (
        "Eres un evaluador experto en sistemas RAG. Dada una PREGUNTA y una lista "
        "de DOCUMENTOS recuperados (cada uno separado por un doble salto de línea), "
        "evalúa qué FRACCIÓN de esos documentos contiene información RELEVANTE y ÚTIL "
        "para responder la pregunta. "
        "Puntúa la PRECISIÓN de 0.0 a 1.0, donde:\n"
        "- 1.0 = TODOS los documentos recuperados son relevantes.\n"
        "- 0.5 = la mitad son relevantes.\n"
        "- 0.0 = NINGUNO es relevante.\n"
        "Cuenta mentalmente cuántos documentos son relevantes y divide por el total. "
        'Devuelve SOLO JSON: {"score": <float>, "reason": "<breve justificación en español>"}.'
    )
    user = (
        f"PREGUNTA:\n{question}\n\n"
        f"DOCUMENTOS recuperados:\n{context_text}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "precision")


def recall(run, example) -> dict:
    """Evalúa si los documentos recuperados cubren TODA la información necesaria.

    Recall = ¿contienen los documentos TODO lo necesario para responder completamente?
    El juez puntúa de 0.0 (información insuficiente) a 1.0 (cobertura total).
    """
    contexts = _get(run.outputs, "contexts", "context", "documents", default=[])
    if isinstance(contexts, list):
        context_text = "\n\n".join(str(c) for c in contexts)
    else:
        context_text = str(contexts)

    question = ""
    if example is not None and example.inputs:
        question = _get(example.inputs, "question", "query", "input")
    elif run.inputs:
        question = _get(run.inputs, "question", "query", "input")

    reference = ""
    if example is not None and example.outputs:
        reference = _get(example.outputs, "answer", "response", "output")

    ref_block = f"\nRespuesta de referencia:\n{reference}\n" if reference else ""

    system = (
        "Eres un evaluador experto en sistemas RAG. Dada una PREGUNTA y los "
        "DOCUMENTOS recuperados, evalúa si esos documentos contienen TODA la "
        "información necesaria para responder la pregunta de forma COMPLETA y CORRECTA. "
        "Puntúa el RECALL de 0.0 a 1.0, donde:\n"
        "- 1.0 = los documentos contienen TODA la información necesaria.\n"
        "- 0.5 = contienen aproximadamente la mitad de lo necesario.\n"
        "- 0.0 = no contienen NADA útil o falta información crítica.\n"
        "Si se proporciona una respuesta de referencia, úsala para verificar qué "
        "información es necesaria y si los documentos la cubren. "
        'Devuelve SOLO JSON: {"score": <float>, "reason": "<breve justificación en español>"}.'
    )
    user = (
        f"PREGUNTA:\n{question}\n"
        f"{ref_block}"
        f"DOCUMENTOS recuperados:\n{context_text}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "recall")


def faithfulness(run, example) -> dict:
    """Evalúa si TODAS las afirmaciones en la respuesta son directamente inferibles del contexto.

    A diferencia de groundedness (que verifica respaldo general), faithfulness es más
    estricto: cada afirmación individual debe poder extraerse del contexto sin
    añadir información externa ni contradicciones.
    """
    prediction = _get(run.outputs, "answer", "response", "output")
    contexts = _get(run.outputs, "contexts", "context", "documents", default=[])
    if isinstance(contexts, list):
        context_text = "\n\n".join(str(c) for c in contexts)
    else:
        context_text = str(contexts)

    system = (
        "Eres un evaluador experto en consistencia factual de sistemas RAG. "
        "Dado un CONTEXTO recuperado y una RESPUESTA generada, descompón la "
        "respuesta en afirmaciones individuales. Para CADA afirmación, verifica "
        "si se puede INFERIR DIRECTAMENTE del contexto, sin información externa.\n\n"
        "Puntúa la FIDELIDAD (faithfulness) de 0.0 a 1.0, donde:\n"
        "- 1.0 = TODAS las afirmaciones son directamente inferibles del contexto.\n"
        "- 0.5 = al menos la mitad son inferibles.\n"
        "- 0.0 = NINGUNA afirmación es inferible (inventada o contradictoria).\n"
        "Penaliza cualquier contradicción entre la respuesta y el contexto.\n"
        "Devuelve SOLO JSON: {\"score\": <float>, \"reason\": \"<breve en español>\"}."
    )
    user = (
        f"CONTEXTO:\n{context_text}\n\n"
        f"RESPUESTA:\n{prediction}\n\n"
        f"Devuelve el JSON."
    )
    return _judge(system, user, "faithfulness")


def threshold(run, example) -> dict:
    """Evalúa si el sistema supera un umbral mínimo en todas las dimensiones.

    Toma las puntuaciones individuales de los otros evaluadores (inyectadas en
    run.outputs) y devuelve 1.0 si TODAS superan el threshold, 0.0 si alguna falla.
    El threshold por defecto es 0.7 (configurable via run.outputs['_threshold']).
    """
    threshold_val = float(_get(run.outputs, "_threshold", default="0.7"))
    scores = []
    for key in ("correctness", "groundedness", "context_relevance", "helpfulness", "precision", "recall", "faithfulness"):
        val = _get(run.outputs, key)
        if val != "":
            try:
                scores.append(float(val))
            except (TypeError, ValueError):
                pass
    if not scores:
        return {"key": "threshold", "score": 0.0, "comment": "No hay puntuaciones para evaluar"}

    passed = all(s >= threshold_val for s in scores)
    min_score = min(scores)
    mean_score = sum(scores) / len(scores)
    return {
        "key": "threshold",
        "score": 1.0 if passed else 0.0,
        "comment": (
            f"threshold={threshold_val:.2f} | "
            f"passed={passed} | "
            f"min={min_score:.3f} | "
            f"mean={mean_score:.3f} | "
            f"scores={ {k: round(v, 3) for k, v in zip(('correctness','groundedness','context_relevance','helpfulness','precision','recall','faithfulness'), scores)} }"
        ),
    }


ALL_EVALUATORS = [correctness, groundedness, context_relevance, helpfulness, precision, recall, faithfulness, threshold]


def judge_pair(
    question: str,
    answer_a: str,
    answer_b: str,
    reference: Optional[str] = None,
) -> dict:
    """Comparador A/B head-to-head.

    Devuelve {"winner": "A"|"B"|"tie", "reason": str, "score_a": float, "score_b": float}.
    Útil para comparar dos variantes de prompt sobre la misma pregunta.
    """
    llm = get_judge_llm()
    ref_block = f"\nRespuesta de referencia (golden):\n{reference}\n" if reference else ""
    system = (
        "Eres un juez experto que compara dos respuestas (A y B) a la misma "
        "pregunta. Evalúa cuál es mejor en correctitud, claridad y utilidad. "
        "Asigna score_a y score_b de 0.0 a 1.0 y declara un ganador: 'A', 'B' o "
        "'tie' (empate). Devuelve SOLO JSON: "
        '{"winner": "A|B|tie", "score_a": <float>, "score_b": <float>, '
        '"reason": "<breve en español>"}.'
    )
    user = (
        f"Pregunta:\n{question}\n"
        f"{ref_block}\n"
        f"Respuesta A:\n{answer_a}\n\n"
        f"Respuesta B:\n{answer_b}\n\n"
        f"Devuelve el JSON."
    )
    raw = llm.invoke([SystemMessage(system), HumanMessage(user)])
    parsed = _extract_json(raw.content)
    return {
        "winner": parsed.get("winner", "tie"),
        "score_a": _clamp01(parsed.get("score_a")),
        "score_b": _clamp01(parsed.get("score_b")),
        "reason": parsed.get("reason") or raw.content[:300],
    }
