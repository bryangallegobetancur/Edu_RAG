import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.ingestion import ingest_pdf, load_vectorstore

from api.schemas import UploadResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "docs"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_vectorstore = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_vectorstore()
    return _vectorstore


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    dest = UPLOAD_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)

    try:
        chunks = ingest_pdf(str(dest))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al indexar el PDF: {exc}")

    return UploadResponse(
        filename=file.filename,
        chunks=chunks,
        message=f"PDF indexado correctamente ({chunks} fragmentos)",
    )


@router.get("")
def list_documents(vs=Depends(get_vectorstore)):
    """Devuelve la lista de documentos cargados en la base vectorial (fuentes unicas)."""
    collection = vs._collection
    results = collection.get(include=["metadatas"])
    sources = {}
    for meta in (results.get("metadatas") or []):
        src = meta.get("source", "desconocido")
        name = Path(src).name if src != "desconocido" else src
        sources[name] = sources.get(name, 0) + 1

    docs = [
        {"name": name, "chunks": count}
        for name, count in sorted(sources.items())
    ]
    return {"documents": docs, "total": len(docs)}
