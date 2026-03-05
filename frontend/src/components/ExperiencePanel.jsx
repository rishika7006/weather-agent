import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const EXPERIENCE_CONTENT = `
## End-to-End User Experience

A walkthrough of how the app works from the moment you open it to getting your answer.

---

### 1. Landing Screen

When you first open the app, you see a clean chat interface with:

- A **welcome message** introducing the Weather Agent
- **Suggestion buttons** with example queries you can click to get started instantly
- A **text input** at the bottom to type your own question

No login, no setup — just start asking.

---

### 2. Sending a Query

You can interact in two ways:

- **Click a suggestion** — Pre-written queries like "What's the weather in New York?" are sent immediately
- **Type your own** — Enter any natural language question and press Enter or click the send button

The input is disabled while the agent is thinking, preventing duplicate requests.

---

### 3. Loading State

After sending a message, you see:

- Your message appears as a **blue bubble** on the right
- A **loading animation** (three bouncing dots) appears on the left, indicating the agent is working
- Behind the scenes, the request flows through: **Frontend → Agent Backend → MCP Server → OpenWeatherMap**

Typical response time is **2-5 seconds** depending on how many tools the agent needs to call.

---

### 4. Receiving the Response

The agent's answer appears as a **dark bubble** on the left with:

- **Markdown formatting** — Bold text, lists, and headers are rendered for readability
- **Tool badges** — Small tags below the message showing which tools were called and with what arguments (e.g., \`get_current_weather(New York)\`)

This transparency lets you see exactly what data the agent fetched to build its answer.

---

### 5. Follow-Up Conversations

The app maintains a rolling **chat history** (last 10 messages), so you can have natural follow-ups:

| You say | What happens |
|---------|-------------|
| "What's the weather in Tokyo?" | Agent calls \`get_current_weather\` |
| "And the forecast?" | Agent remembers Tokyo, calls \`get_weather_forecast\` |
| "How about London instead?" | Agent switches context to London |

The conversation scrolls automatically to keep the latest messages visible.

---

### 6. Error Handling

If something goes wrong, you see a **red error banner** at the bottom of the chat with a clear message:

| Scenario | What you see |
|----------|-------------|
| Backend is down | "Failed to get response. Is the backend running?" |
| Invalid city name | Agent responds with a friendly "I couldn't find that city" message |
| API rate limit hit | Server error message from the backend |
| Empty message | Send button is disabled — can't submit blank input |

Errors don't clear your conversation — you can fix the issue and keep chatting.

---

### 7. Multi-City & Multi-Tool Queries

The agent handles complex requests that require multiple tool calls:

| Query | Tools called |
|-------|-------------|
| "Compare weather in London and Paris" | \`get_current_weather\` × 2 |
| "Forecast and air quality for Berlin" | \`get_weather_forecast\` + \`get_air_quality\` |
| "Weather, forecast, and air quality for NYC" | All 3 tools |

The agent calls all necessary tools, then synthesizes everything into a single, cohesive response.

---

### Interface Overview

| Element | Location | Purpose |
|---------|----------|---------|
| Header | Top | App title and navigation tabs |
| Tab bar | Top right | Switch between Chat, Help, Architecture, Agent, and Experience |
| Chat area | Center | Scrollable message history |
| Suggestion chips | Center (empty state) | Quick-start example queries |
| Input bar | Bottom | Text field + send button |
| Tool badges | Below agent messages | Shows which tools were invoked |
| Error banner | Bottom of chat | Displays error messages |
`;

export default function ExperiencePanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{EXPERIENCE_CONTENT}</Markdown>
    </div>
  );
}
