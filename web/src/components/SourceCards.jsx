import { useState } from "react";

function sourceLabel(src) {
  const name = src?.source?.split(/[\\/]/).pop() || "desconocida";
  return name;
}

export default function SourceCards({ sources }) {
  const [openIndex, setOpenIndex] = useState(null);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources">
      <div className="sources-title">Fuentes recuperadas ({sources.length})</div>
      <div className="sources-list">
        {sources.map((s, i) => {
          const open = openIndex === i;
          return (
            <div key={i} className={`source-card ${open ? "open" : ""}`}>
              <button
                className="source-header"
                onClick={() => setOpenIndex(open ? null : i)}
              >
                <span className="source-icon">📑</span>
                <span className="source-name">{sourceLabel(s)}</span>
                {s.page != null && <span className="source-page">p. {s.page}</span>}
                <span className="source-chevron">{open ? "▾" : "▸"}</span>
              </button>
              {open && (
                <div className="source-content">
                  {s.content}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
