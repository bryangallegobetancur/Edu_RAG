import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";
import ChatInput from "./ChatInput.jsx";

export default function ChatView({ messages, isStreaming, onSend, onStop, onClear, onRate, documents }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-view">
      <div className="messages">
        {isEmpty && (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <h2>Asistente del Proceso Administrativo</h2>
            <p>
              Pregúntame sobre planificación, organización, dirección y control.
              Responderé basándome en los materiales del curso y te mostraré las
              fuentes exactas (archivo y página) de donde proviene cada respuesta.
            </p>
            {documents.length > 0 && (
              <div className="doc-list">
                <div className="doc-list-title">Documentos indexados ({documents.length})</div>
                {documents.map((d, i) => (
                  <div key={i} className="doc-item">
                    <span className="doc-item-icon">📄</span>
                    <span className="doc-item-name">{d.name}</span>
                    <span className="doc-item-chunks">{d.chunks} fragmentos</span>
                  </div>
                ))}
              </div>
            )}
            <div className="suggestions">
              <button onClick={() => onSend("¿Cuáles son las etapas del proceso administrativo?")}>
                ¿Cuáles son las etapas del proceso administrativo?
              </button>
              <button onClick={() => onSend("Explica la función de planeación y sus tipos")}>
                Explica la función de planeación y sus tipos
              </button>
              <button onClick={() => onSend("¿Qué es la delegación y por qué es importante?")}>
                ¿Qué es la delegación y por qué es importante?
              </button>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} messageIndex={i} onRate={onRate} />
        ))}
        <div ref={endRef} />
      </div>

      <div className="chat-footer">
        {messages.length > 0 && !isStreaming && (
          <button className="clear-btn" onClick={onClear} title="Limpiar conversación">
            🗑 Nueva conversación
          </button>
        )}
        <ChatInput onSend={onSend} onStop={onStop} isStreaming={isStreaming} />
        <div className="chat-hint">
          {documents.length > 0 ? (
            <>Basado en {documents.length} documento{documents.length !== 1 ? "s" : ""} · {documents.reduce((s, d) => s + d.chunks, 0)} fragmentos</>
          ) : (
            "El asistente responde solo con el material indexado. Si no hay datos, lo indicará sin inventar."
          )}
        </div>
      </div>
    </div>
  );
}
