from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENCODE_GO_API_KEY,
    OPENCODE_GO_MODEL,
    OPENCODE_GO_BASE_URL,
    TOP_K,
)

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil. Responde la pregunta basándote SOLO en el contexto proporcionado. "
               "Si el contexto no contiene información suficiente para responder, di 'No tengo suficiente "
               "información para responder esta pregunta' y no inventes nada. "
               "Responde en español.\n\n"
               "Contexto:\n{context}"),
    ("human", "{question}"),
])


def get_llm(streaming: bool = False):
    if LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0,
            streaming=streaming,
        )
    elif LLM_PROVIDER == "opencode-go":
        return ChatOpenAI(
            model=OPENCODE_GO_MODEL,
            api_key=OPENCODE_GO_API_KEY,
            base_url=OPENCODE_GO_BASE_URL,
            temperature=0,
            streaming=streaming,
        )
    else:
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[Fuente: {doc.metadata.get('source', 'desconocida')} | "
        f"Página: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
        for doc in docs
    )


def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": TOP_K},
    )
    llm = get_llm()

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


def ask(vectorstore, question: str):
    chain = build_rag_chain(vectorstore)
    response = chain.invoke(question)
    return response


def ask_with_sources(vectorstore, question: str):
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    docs = retriever.invoke(question)

    print(f"\nRecuperados {len(docs)} fragmentos:\n")
    for i, doc in enumerate(docs, 1):
        src = doc.metadata.get("source", "?")
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  [{i}] {src} (p.{page}): {preview}...")

    chain = build_rag_chain(vectorstore)
    return chain.invoke(question)


def serialize_sources(docs):
    return [
        {
            "source": doc.metadata.get("source", "desconocida"),
            "page": doc.metadata.get("page"),
            "content": doc.page_content,
        }
        for doc in docs
    ]


def ask_stream_with_sources(vectorstore, question: str):
    """Recupera las fuentes y devuelve (sources, generador de tokens).

    El generador emite tokens del LLM en streaming para UX tipo chat.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    docs = retriever.invoke(question)
    sources = serialize_sources(docs)
    context = format_docs(docs)

    llm = get_llm(streaming=True)
    chain = RAG_PROMPT | llm | StrOutputParser()

    def token_generator():
        for chunk in chain.stream({"context": context, "question": question}):
            yield chunk

    return sources, token_generator()
