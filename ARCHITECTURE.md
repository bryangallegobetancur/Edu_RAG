# Arquitectura del RAG

```mermaid
flowchart TB
    subgraph INGESTION["📥 INGESTIÓN DE DOCUMENTOS"]
        direction TB
        FILES["PDFs / TXTs"]
        LOADER["DirectoryLoader<br/><i>PyPDFLoader + TextLoader</i>"]
        SPLITTER["RecursiveCharacterTextSplitter<br/><i>chunk=1000 | overlap=200</i>"]
        EMB_IN["HuggingFaceEmbeddings<br/><i>all-MiniLM-L6-v2 (CPU)</i>"]
        FILES --> LOADER --> SPLITTER --> EMB_IN
    end

    subgraph STORAGE["🗄️ ALMACENAMIENTO VECTORIAL"]
        CHROMA["ChromaDB<br/><i>chroma_db/ (disco local)</i>"]
    end

    subgraph QUERY["🔍 CONSULTA (RAG)"]
        direction TB
        QUESTION["❓ Pregunta del usuario"]
        RETRIEVER["Retriever<br/><i>top_k=5</i>"]
        FORMAT["format_docs()<br/><i>concatena fragmentos + metadata</i>"]
        PROMPT["ChatPromptTemplate<br/><i>system + context + question</i>"]
        QUESTION --> RETRIEVER --> FORMAT --> PROMPT
    end

    subgraph LLM["🤖 LLM"]
        OPENCODE["ChatOpenAI (compatible)<br/><b>DeepSeek V4 Flash</b><br/><i>via opencode-go</i>"]
        API["https://opencode.ai/zen/go/v1"]
        PROMPT --> OPENCODE --> API --> OPENCODE
    end

    subgraph OBSERVABILITY["📊 OBSERVABILIDAD"]
        LS["LangSmith<br/><i>proyecto: RAG_testing</i>"]
    end

    OUTPUT["✅ Respuesta final"]
    CLIENT["🖥️ CLI: main.py"]

    INGESTION --> STORAGE
    STORAGE --> RETRIEVER
    OPENCODE --> OUTPUT --> CLIENT

    INGESTION -.->|tracing| LS
    QUERY -.->|tracing| LS
    LLM -.->|tracing| LS
    CLIENT -.-> LS

    %% Styles
    style INGESTION fill:#1e3a8a,stroke:#3b82f6,color:#fff
    style STORAGE fill:#1e40af,stroke:#60a5fa,color:#fff
    style QUERY fill:#1e3a8a,stroke:#3b82f6,color:#fff
    style LLM fill:#6d28d9,stroke:#8b5cf6,color:#fff
    style OBSERVABILITY fill:#065f46,stroke:#10b981,color:#fff
    style OUTPUT fill:#16a34a,stroke:#22c55e,color:#fff
    style CLIENT fill:#374151,stroke:#9ca3af,color:#fff
```

## Flujo de datos

| Etapa           | Herramienta                        | Detalle                                          |
|-----------------|------------------------------------|--------------------------------------------------|
| **Carga**       | `DirectoryLoader`                  | PDFs (`PyPDFLoader`) + TXTs (`TextLoader`)       |
| **Chunking**    | `RecursiveCharacterTextSplitter`   | 1000 chars, solapamiento 200                     |
| **Embeddings**  | `HuggingFaceEmbeddings`            | `all-MiniLM-L6-v2`, CPU, normalizado             |
| **Vector DB**   | `ChromaDB`                         | Persistente en `chroma_db/`                      |
| **Retrieval**   | `vectorstore.as_retriever(k=5)`    | Búsqueda por similitud de coseno                 |
| **Prompt**      | `ChatPromptTemplate`               | System prompt en español + contexto + pregunta   |
| **LLM**         | `ChatOpenAI` (compatible)          | `deepseek-v4-flash` via `opencode-go`            |
| **Output**      | `StrOutputParser`                  | Respuesta en texto plano                         |
| **Tracing**     | `LangSmith`                        | Proyecto `RAG_testing`                           |

## Capa Web (front-end + API)

```mermaid
flowchart LR
    BROWSER["🖥️ React + Vite<br/>web/"] -->|SSE streaming| API["FastAPI<br/>api/server.py"]
    API -->|POST /api/chat| STREAM["ask_stream_with_sources<br/>sources + tokens"]
    API -->|POST /api/documents/upload| INGEST["ingest_pdf<br/>indexa PDF individual"]
    STREAM --> RET["Retriever + LLM"]
    INGEST --> CHROMA2["ChromaDB"]
    RET --> CHROMA2
```

| Componente      | Carpeta        | Detalle                                                       |
|-----------------|----------------|---------------------------------------------------------------|
| **Front-end**   | `web/`         | React 18 + Vite. Chat con streaming, citas, upload PDF, tema. |
| **API**         | `api/`         | FastAPI. Rutas `/api/chat` (SSE) y `/api/documents/upload`.   |
| **Streaming**   | SSE            | Server-Sent Events: evento `sources` + `token`*N + `done`.    |

### Ejecutar el backend (FastAPI)

```bash
pip install -r requirements.txt   # incluye fastapi, uvicorn, python-multipart
uvicorn api.server:app --reload --port 8000
```

### Ejecutar el front-end (React + Vite)

```bash
cd web
npm install
npm run dev    # http://localhost:5173 (proxy /api -> localhost:8000)
```

> Primero indexa los materiales del curso con el CLI si la base vectorial
> aún no existe: `python main.py ingest <docs_dir>`.

### Build de producción del front-end

```bash
cd web
npm run build    # genera web/dist/
```


## Stack tecnológico

```
┌─────────────────────────────────────────────────────┐
│                    LangChain 1.3                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ langchain-   │  │ langchain-   │  │ langchain-  │ │
│  │ community    │  │ chroma       │  │ huggingface │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ langchain-   │  │ langchain-   │  │ langchain-  │ │
│  │ openai       │  │ ollama       │  │ text_split  │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
├─────────────────────────────────────────────────────┤
│  ChromaDB  │  sentence-transformers  │  LangSmith   │
├─────────────────────────────────────────────────────┤
│  DeepSeek V4 Flash  │  OpenCode Go  │  HuggingFace │
└─────────────────────────────────────────────────────┘
```
