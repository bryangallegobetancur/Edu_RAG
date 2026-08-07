# Arquitectura del RAG

```mermaid
flowchart TB
    subgraph CLIENT["🖥️  CLIENTES"]
        direction LR
        CLI["CLI<br/>python main.py"]
        BROWSER["Navegador React + Vite<br/>localhost:5173"]
    end

    subgraph API["🌐  API FastAPI  :8000"]
        direction LR
        CHAT["POST /api/chat<br/>SSE streaming"]
        UPLOAD["POST /api/documents/upload<br/>PDF individual"]
    end

    subgraph INGESTION["📥  INGESTIÓN"]
        direction LR
        FILES["PDFs / TXTs"] --> LOADER["DirectoryLoader<br/><i>PyPDFLoader + TextLoader</i>"] --> SPLITTER["RecursiveCharacterTextSplitter<br/><i>chunk=1000 | overlap=200</i>"] --> EMB_IN["HuggingFaceEmbeddings<br/><i>all-MiniLM-L6-v2  (CPU)</i>"]
    end

    subgraph STORAGE["🗄️  ChromaDB  chroma_db/"]
        CHROMA["Colección de vectores<br/><i>similitud coseno</i>"]
    end

    subgraph RETRIEVAL["🔍  RETRIEVAL"]
        RETR["Retriever top_k=5<br/><i>similitud coseno</i>"]
        FORMAT["format_docs()<br/><i>concatena fragmentos + metadata</i>"]
    end

    subgraph GEN["🧠  GENERACIÓN"]
        PROMPT["ChatPromptTemplate<br/><i>system + context + question</i>"]
        LLM["ChatOpenAI compatible<br/><b>DeepSeek V4 Flash</b><br/><i>via opencode-go</i>"]
        OUTPUT["StrOutputParser"]
    end

    subgraph EVAL["⚖️  EVALUACIÓN  LLM-as-a-Judge (qwen3.7-plus)"]
        direction LR
        J_LLM["qwen3.7-plus<br/><i>via opencode-go</i>"]
        CORR["correctness<br/><i>vs respuesta golden</i>"]
        GROUND["groundedness<br/><i>anti-alucinación</i>"]
        CTX["context_relevance<br/><i>chunks útiles</i>"]
        HELP["helpfulness<br/><i>claridad / concisión</i>"]
        PREC["precision<br/><i>docs relevantes / total</i>"]
        RECALL["recall<br/><i>cobertura completa</i>"]
        FAITH["faithfulness<br/><i>afirmación x afirmación</i>"]
        THRESH["threshold<br/><i>todas >= 0.7 → 1.0</i>"]
        AB["A/B pair judge<br/><i>compara 2 prompts</i>"]
        J_LLM --> CORR
        J_LLM --> GROUND
        J_LLM --> CTX
        J_LLM --> HELP
        J_LLM --> PREC
        J_LLM --> RECALL
        J_LLM --> FAITH
        J_LLM --> AB
        CORR --> THRESH
        GROUND --> THRESH
        CTX --> THRESH
        HELP --> THRESH
        PREC --> THRESH
        RECALL --> THRESH
        FAITH --> THRESH
    end

    subgraph OBS["📊  LangSmith"]
        TRACE["Tracing automático"]
        DATASET["Dataset golden<br/>RAG_eval_qa"]
        EXP["Experimentos<br/>rag-eval"]
    end

    %% Flujo principal
    CLI --> API
    BROWSER -->|SSE streaming| CHAT
    BROWSER --> UPLOAD
    UPLOAD --> EMB_IN
    CHAT --> RETR

    INGESTION --> STORAGE
    STORAGE --> RETR
    RETR --> FORMAT
    FORMAT --> PROMPT
    PROMPT --> LLM
    LLM --> OUTPUT
    OUTPUT --> CHAT
    OUTPUT --> CLI

    %% Evaluación
    FILES -->|genera Q/A| J_LLM
    J_LLM -->|crea ejemplos| DATASET
    DATASET -->|experimentos| CORR
    DATASET -->|experimentos| GROUND
    DATASET -->|experimentos| CTX
    DATASET -->|experimentos| HELP
    DATASET -->|experimentos| PREC
    DATASET -->|experimentos| RECALL
    DATASET -->|experimentos| FAITH
    DATASET -->|experimentos| AB
    CORR --> EXP
    GROUND --> EXP
    CTX --> EXP
    HELP --> EXP
    PREC --> EXP
    RECALL --> EXP
    FAITH --> EXP
    THRESH --> EXP
    AB --> EXP

    %% Tracing
    INGESTION -.->|tracing| TRACE
    RETRIEVAL -.->|tracing| TRACE
    LLM -.->|tracing| TRACE
    EXP --> TRACE

    %% Styles
    style CLIENT fill:#374151,stroke:#9ca3af,color:#fff
    style API fill:#1e40af,stroke:#60a5fa,color:#fff
    style INGESTION fill:#1e3a8a,stroke:#3b82f6,color:#fff
    style STORAGE fill:#1e40af,stroke:#60a5fa,color:#fff
    style RETRIEVAL fill:#1e3a8a,stroke:#3b82f6,color:#fff
    style GEN fill:#6d28d9,stroke:#8b5cf6,color:#fff
    style EVAL fill:#ea580c,stroke:#f97316,color:#fff
    style OBS fill:#065f46,stroke:#10b981,color:#fff
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

## Evaluación con LangSmith

### Métricas (LLM-as-a-Judge con `qwen3.7-plus`)

| # | Métrica             | Qué evalúa                                                              | Escala |
|---|---------------------|-------------------------------------------------------------------------|--------|
| 1 | `correctness`       | Similitud de la respuesta generada vs. respuesta golden de referencia   | 0.0–1.0 |
| 2 | `groundedness`      | Qué tanto se respalda la respuesta en los documentos recuperados (anti-alucinación) | 0.0–1.0 |
| 3 | `context_relevance` | Qué tan relevantes son los chunks recuperados para la pregunta          | 0.0–1.0 |
| 4 | `helpfulness`       | Utilidad, claridad y concisión de la respuesta para el usuario          | 0.0–1.0 |
| 5 | `precision`         | Fracción de los documentos recuperados que son realmente relevantes     | 0.0–1.0 |
| 6 | `recall`            | Si los documentos recuperados contienen TODA la info necesaria para responder | 0.0–1.0 |
| 7 | `faithfulness`      | Cada afirmación individual de la respuesta es directamente inferible del contexto (más estricto que groundedness) | 0.0–1.0 |
| 8 | `threshold`         | Compuesto binario: 1.0 si TODAS las 7 métricas >= umbral (defecto 0.7), 0.0 si alguna falla | 0 o 1 |
| — | **A/B pair judge**  | Compara dos respuestas (de distintos prompts) y declara ganador con scores | winner + scores |

### Flujo de evaluación

```bash
# 1. Generar dataset golden sintético desde tus PDFs
python evaluate.py gen-dataset --docs-dir docs --n-questions 10

# 2. Ejecutar el RAG sobre el dataset y medir las 4 métricas
python evaluate.py run --dataset RAG_eval_qa

# 3. Comparar dos system prompts (A/B testing)
python evaluate.py ab --dataset RAG_eval_qa --prompt-a prompt_a.txt --prompt-b prompt_b.txt
```

- **Dataset**: los pares pregunta/respuesta golden se generan automáticamente con el juez (`qwen3.7-plus`) desde fragmentos de tus PDFs y se suben a LangSmith.
- **Experimento**: `evaluate.py run` ejecuta el RAG sobre cada pregunta del dataset, invoca los 4 jueces, y publica los resultados en LangSmith.
- **A/B**: `evaluate.py ab` compara dos system prompts distintos sobre el mismo dataset con un juez pareado que decide ganador.

## Capa Web (front-end + API)

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
