import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENCODE_GO_API_KEY = os.getenv("OPENCODE_GO_API_KEY")
OPENCODE_GO_MODEL = os.getenv("OPENCODE_GO_MODEL", "deepseek-v4-flash")
OPENCODE_GO_BASE_URL = os.getenv("OPENCODE_GO_BASE_URL", "https://api.opencode.ai/v1")

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "mi-rag")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

CHROMA_PERSIST_DIR = "chroma_db"
CHUNK_SIZE = 3500
CHUNK_OVERLAP = 500
TOP_K = 5

JUDGE_PROVIDER = os.getenv("JUDGE_PROVIDER", "opencode-go")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "qwen3.7-plus")
JUDGE_TEMPERATURE = float(os.getenv("JUDGE_TEMPERATURE", "0"))

LANGSMITH_EVAL_DATASET = os.getenv("LANGSMITH_EVAL_DATASET", "RAG_eval_qa")
LANGSMITH_EVAL_EXPERIMENT = os.getenv("LANGSMITH_EVAL_EXPERIMENT", "rag-eval")
