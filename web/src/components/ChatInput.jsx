import { useRef, useEffect } from "react";

export default function ChatInput({ onSend, onStop, isStreaming }) {
  const inputRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!isStreaming) inputRef.current?.focus();
  }, [isStreaming]);

  function autoResize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }

  function handleSubmit(e) {
    e?.preventDefault();
    const value = textareaRef.current?.value ?? "";
    if (!value.trim()) return;
    onSend(value);
    if (textareaRef.current) {
      textareaRef.current.value = "";
      autoResize();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <textarea
        ref={textareaRef}
        onInput={autoResize}
        onKeyDown={handleKeyDown}
        placeholder="Pregunta sobre el Proceso Administrativo…  (Enter para enviar, Shift+Enter para salto de línea)"
        rows={1}
        disabled={isStreaming}
      />
      {isStreaming ? (
        <button type="button" className="send-btn stop" onClick={onStop}>
          ⏹ Detener
        </button>
      ) : (
        <button type="submit" className="send-btn">
          Enviar ➤
        </button>
      )}
    </form>
  );
}
