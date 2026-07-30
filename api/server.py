from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat, documents


def create_app() -> FastAPI:
    app = FastAPI(title="RAG API", description="Asistente RAG para Introducción al Proceso Administrativo")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(documents.router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
