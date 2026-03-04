export default function MessageBubble({ role, content, toolCalls }) {
  return (
    <div className={`message ${role}`}>
      <div className="message-avatar">
        {role === "assistant" ? "\u2601\uFE0F" : "\uD83D\uDC64"}
      </div>
      <div>
        <div className="message-content">
          {content.split("\n").map((line, i) => (
            <span key={i}>
              {line}
              {i < content.split("\n").length - 1 && <br />}
            </span>
          ))}
        </div>
        {toolCalls && toolCalls.length > 0 && (
          <div className="tool-calls">
            {toolCalls.map((tc, i) => (
              <span key={i} className="tool-badge">
                {tc.tool}({Object.values(tc.args).join(", ")})
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
