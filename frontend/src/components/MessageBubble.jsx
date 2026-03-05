import Markdown from "react-markdown";

export default function MessageBubble({ role, content, toolCalls, cached, fallback }) {
  return (
    <div className={`message ${role}`}>
      <div className="message-avatar">
        {role === "assistant" ? "\u2601\uFE0F" : "\uD83D\uDC64"}
      </div>
      <div>
        <div className="message-content">
          {role === "assistant" ? (
            <Markdown>{content}</Markdown>
          ) : (
            content
          )}
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
        {(cached || fallback) && (
          <div className="status-badges">
            {cached && <span className="cached-badge">(cached)</span>}
            {fallback && <span className="fallback-badge">(fallback - MCP server unavailable)</span>}
          </div>
        )}
      </div>
    </div>
  );
}
