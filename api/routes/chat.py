import json
import os

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.ingestion import load_vectorstore
from src.retrieval import ask_stream_with_sources

from api.schemas import ChatRequest, FeedbackRequest

router = APIRouter(prefix="/api", tags=["chat"])

_vectorstore = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_vectorstore()
    return _vectorstore


@router.post("/chat")
def chat(req: ChatRequest, vs=Depends(get_vectorstore)):
    sources, token_gen = ask_stream_with_sources(vs, req.question)

    def event_stream():
        yield f"data: {json.dumps({'type': 'sources', 'data': sources}, ensure_ascii=False)}\n\n"
        try:
            for tok in token_gen:
                if not tok:
                    continue
                yield f"data: {json.dumps({'type': 'token', 'data': tok}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'data': str(exc)}, ensure_ascii=False)}\n\n"
            return
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/feedback")
def feedback(req: FeedbackRequest):
    score_value = req.score
    comment = "👍 Thumbs up" if score_value == 1 else "👎 Thumbs down"

    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key:
        try:
            from langsmith import Client
            client = Client()
            client.create_feedback(
                key="user-rating",
                score=score_value,
                comment=comment,
            )
        except Exception:
            pass

    return {"status": "ok", "score": score_value}
