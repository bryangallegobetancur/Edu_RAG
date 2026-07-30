import SourceCards from "./SourceCards.jsx";

function renderContent(content) {
  if (!content) return null;
  return content.split("\n").map((line, i) => (
    <span key={i}>
      {line || "\u00A0"}
      {i < content.split("\n").length - 1 && <br />}
    </span>
  ));
}

export default function MessageBubble({ message, messageIndex, onRate }) {
  const isUser = message.role === "user";
  const showFeedback = !isUser && !message.pending && message.content;

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? "\uD83E\uDDD1\u200D\uD83C\uDF93" : "\uD83E\uDD16"}</div>
      <div className="bubble">
        <div className="bubble-content">
          {renderContent(message.content)}
          {message.pending && !message.content && (
            <span className="typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </span>
          )}
          {message.pending && message.content && <span className="cursor">{"\u258D"}</span>}
        </div>
        {!isUser && !message.pending && message.sources?.length > 0 && (
          <SourceCards sources={message.sources} />
        )}
        {showFeedback && (
          <div className="feedback-row">
            <button
              className={`thumb-btn ${message.feedback === 1 ? "active up" : ""}`}
              onClick={() => onRate?.(messageIndex, 1)}
              disabled={message.feedback !== null}
              title="Respuesta correcta"
            >
              {"\uD83D\uDC4D"}
            </button>
            <button
              className={`thumb-btn ${message.feedback === 0 ? "active down" : ""}`}
              onClick={() => onRate?.(messageIndex, 0)}
              disabled={message.feedback !== null}
              title="Respuesta incorrecta"
            >
              {"\uD83D\uDC4E"}
            </button>
            {message.feedback !== null && (
              <span className="feedback-thanks">Gracias por tu valoración</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
