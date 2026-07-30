import { useRef, useState } from "react";
import { uploadPdf } from "../lib/api.js";

export default function PdfUpload({ onUploaded }) {
  const inputRef = useRef(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [busy, setBusy] = useState(false);

  async function handleFiles(files) {
    const file = files?.[0];
    if (!file) return;
    setBusy(true);
    setProgress(0);
    setStatus({ type: "info", text: `Subiendo ${file.name}…` });
    try {
      const res = await uploadPdf(file, setProgress);
      setStatus({ type: "ok", text: res.message });
      onUploaded?.(res);
    } catch (err) {
      setStatus({ type: "error", text: err.message || "Error al subir el PDF" });
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="pdf-upload">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        onChange={(e) => handleFiles(e.target.files)}
        hidden
      />
      <button
        className="upload-btn"
        onClick={() => inputRef.current?.click()}
        disabled={busy}
        title="Subir un PDF del curso al conocimiento del asistente"
      >
        📄 Subir PDF
      </button>
      {busy && progress > 0 && <span className="progress">{progress}%</span>}
      {status && (
        <span className={`upload-status ${status.type}`}>{status.text}</span>
      )}
    </div>
  );
}
