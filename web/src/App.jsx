import { useEffect, useState } from "react";
import ChatView from "./components/ChatView.jsx";
import ThemeToggle from "./components/ThemeToggle.jsx";
import PdfUpload from "./components/PdfUpload.jsx";
import { useChat } from "./hooks/useChat.js";
import { useTheme } from "./hooks/useTheme.js";
import { listDocuments } from "./lib/api.js";

export default function App() {
  const { messages, isStreaming, send, stop, clear, rateMessage } = useChat();
  const { theme, toggle } = useTheme();
  const [docs, setDocs] = useState([]);

  const refreshDocs = () => {
    listDocuments()
      .then((data) => setDocs(data.documents || []))
      .catch(() => {});
  };

  useEffect(() => {
    refreshDocs();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="brand-icon">🎓</span>
          <div className="brand-text">
            <h1>Proceso Administrativo</h1>
            <span className="brand-sub">Asistente RAG · Introducción al Proceso Administrativo</span>
          </div>
        </div>
        <div className="header-actions">
          <PdfUpload onUploaded={refreshDocs} />
          <ThemeToggle theme={theme} onToggle={toggle} />
        </div>
      </header>

      <main className="app-main">
        <ChatView
          messages={messages}
          isStreaming={isStreaming}
          onSend={send}
          onStop={stop}
          onClear={clear}
          onRate={rateMessage}
          documents={docs}
        />
      </main>
    </div>
  );
}
