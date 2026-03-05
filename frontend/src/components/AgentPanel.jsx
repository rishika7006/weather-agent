import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AGENT_CONTENT = `
## LLM Agent Setup

The agent backend is the brain of this application. It uses **LangChain** with **Anthropic Claude** to understand your natural language queries and decide which weather tools to call.

---

### How a Request Flows Through the Agent

\`\`\`
1. User sends "What's the weather in Tokyo?"
2. Agent receives the message + recent chat history
3. Claude analyzes the intent via the system prompt
4. Claude decides to call get_current_weather(city="Tokyo")
5. The tool makes an HTTP request to the MCP Server
6. Tool returns structured weather data as a string
7. Claude reads the tool result and writes a friendly response
8. Response is sent back to the frontend
\`\`\`

---

### System Prompt

The agent is initialized with a system prompt that defines its personality and rules:

- **Role** — A helpful weather assistant that provides accurate, friendly, and concise information.
- **Tool awareness** — The prompt tells Claude about all three available tools and when to use each one.
- **Multi-city handling** — If you ask about multiple cities, the agent calls the tool for each city separately.
- **Units** — All temperatures are provided in Fahrenheit.
- **Scope** — If you ask a non-weather question, the agent politely redirects you.
- **Synthesis** — For forecasts, the agent summarizes key trends (warming up, cooling down, rain expected) rather than listing raw numbers.

---

### Tool Definitions

The agent has three tools registered via LangChain's \`@tool\` decorator. Each tool wraps a call to the MCP Server.

#### get_current_weather

| Property | Value |
|----------|-------|
| Parameter | \`city\` (string, required) |
| Calls | \`GET /api/weather/current?city={city}\` |
| Returns | Temperature, feels-like, conditions, humidity, wind speed, pressure, visibility |

#### get_weather_forecast

| Property | Value |
|----------|-------|
| Parameters | \`city\` (string, required), \`days\` (int, 1-5, default 3) |
| Calls | \`GET /api/weather/forecast?city={city}&days={days}\` |
| Returns | Daily high/low temps, conditions, and average humidity for each day |

#### get_air_quality

| Property | Value |
|----------|-------|
| Parameter | \`city\` (string, required) |
| Calls | \`GET /api/weather/air-quality?city={city}\` |
| Returns | AQI rating, PM2.5, PM10, Ozone, NO2, CO levels |

Each tool formats the MCP Server response into a human-readable string that Claude uses to compose its final answer.

---

### LangChain / LangGraph Logic

The agent is built using two key components:

**ChatAnthropic LLM**
- Model: \`claude-sonnet-4-20250514\`
- Temperature: \`0.3\` (low for factual accuracy, slight flexibility for natural phrasing)
- Max tokens: \`1024\`

**create_react_agent (LangGraph)**
The agent uses LangGraph's \`create_react_agent\`, which implements the **ReAct pattern** (Reasoning + Acting):

\`\`\`
Loop:
  1. THINK  — Claude reasons about what to do next
  2. ACT    — Claude calls one or more tools
  3. OBSERVE — Claude reads the tool results
  Repeat until Claude has enough info to respond
  4. RESPOND — Claude writes the final answer
\`\`\`

This means the agent can:
- Call **multiple tools** in sequence (e.g., forecast + air quality)
- Call the **same tool multiple times** (e.g., weather for London and Paris)
- Decide to call **no tools** if the question doesn't need one

---

### Chat History

The agent receives up to the **last 10 messages** as context. This enables follow-up questions like:

- "What's the weather in Tokyo?" → (agent responds)
- "And the forecast?" → The agent remembers you were asking about Tokyo

Messages are converted to LangChain's \`HumanMessage\` and \`AIMessage\` types before being passed to the agent.
`;

export default function AgentPanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{AGENT_CONTENT}</Markdown>
    </div>
  );
}
