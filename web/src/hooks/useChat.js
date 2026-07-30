import { useCallback, useRef, useState } from "react";
import { sendFeedback, streamChat } from "../lib/api.js";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef(null);

  const appendToLast = useCallback((text) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const last = prev[prev.length - 1];
      if (last.role !== "assistant") return prev;
      const next = prev.slice();
      next[next.length - 1] = { ...last, content: last.content + text };
      return next;
    });
  }, []);

  const setLastSources = useCallback((sources) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const last = prev[prev.length - 1];
      if (last.role !== "assistant") return prev;
      const next = prev.slice();
      next[next.length - 1] = { ...last, sources };
      return next;
    });
  }, []);

  const send = useCallback(
    async (question) => {
      if (!question.trim() || isStreaming) return;

      setMessages((prev) => [
        ...prev,
        { role: "user", content: question },
        { role: "assistant", content: "", sources: [], pending: true, feedback: null },
      ]);
      setIsStreaming(true);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        await streamChat(question, {
          onSources: (sources) => setLastSources(sources),
          onToken: (tok) => appendToLast(tok),
          signal: controller.signal,
        });
      } catch (err) {
        if (err.name === "AbortError") {
          appendToLast("\n\n_(detenido)_");
        } else {
          appendToLast(`\n\n⚠️ Error: ${err.message}`);
        }
      } finally {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const next = prev.slice();
          const last = next[next.length - 1];
          if (last?.role === "assistant") {
            next[next.length - 1] = { ...last, pending: false };
          }
          return next;
        });
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [isStreaming, appendToLast, setLastSources]
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const clear = useCallback(() => {
    if (isStreaming) return;
    setMessages([]);
  }, [isStreaming]);

  const rateMessage = useCallback(
    async (msgIndex, score) => {
      const msg = messages[msgIndex];
      if (!msg || msg.role !== "assistant" || msg.feedback !== null) return;

      const userMsg = messages[msgIndex - 1];
      const question = userMsg?.role === "user" ? userMsg.content : "";

      setMessages((prev) => {
        const next = prev.slice();
        next[msgIndex] = { ...next[msgIndex], feedback: score };
        return next;
      });

      try {
        await sendFeedback(question, msg.content, score);
      } catch {
        // silently ignore
      }
    },
    [messages]
  );

  return { messages, isStreaming, send, stop, clear, rateMessage };
}
