import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const ARCHITECTURE_CONTENT = `
## MCP Server Architecture

The MCP (Microservice Communication Protocol) Server sits between the AI agent and the external OpenWeatherMap API. It acts as a dedicated API wrapper that normalizes, simplifies, and isolates all external weather data access.

---

### How It Works

\`\`\`
User Query
   |
   v
React Frontend  ---->  Agent Backend (LangChain + Claude)
                              |
                              |  The agent decides which tool(s) to call
                              v
                        MCP Server (FastAPI, Port 8001)
                              |
                              |  WeatherService (LFU cache)
                              |       |
                              |       v
                              |  WeatherProvider (pluggable)
                              |       |
                              |  1. Geocodes city name -> lat/lon
                              |  2. Calls weather API
                              |  3. Normalizes the response
                              v
                        Weather API (OpenWeatherMap, etc.)
\`\`\`

The MCP Server exposes three clean endpoints:

| Endpoint | Purpose |
|----------|---------|
| \`/api/weather/current\` | Current conditions for a city |
| \`/api/weather/forecast\` | Multi-day forecast (1-5 days) |
| \`/api/weather/air-quality\` | Air quality index and pollutants |

Each endpoint handles geocoding internally — the caller only needs to provide a city name.

---

### Key Design Decisions

- **Geocoding abstraction** — The MCP Server converts city names to coordinates behind the scenes, so neither the agent nor the frontend ever deals with lat/lon.
- **Response normalization** — Raw OpenWeatherMap responses are transformed into clean, consistent JSON with only the fields that matter.
- **Forecast aggregation** — The 3-hour interval data from OpenWeatherMap is grouped by day and summarized (high/low temps, most frequent condition).
- **Imperial units** — All temperatures are returned in Fahrenheit and wind speeds in mph by default.

---

### Pros

**Separation of concerns**
The agent backend knows nothing about the weather provider. It just calls clean internal endpoints. The MCP Server uses a pluggable provider abstraction — switching providers is a one-line env change (see the Improvements tab).

**Independent scalability**
The MCP Server can be scaled, cached, or rate-limited independently from the agent backend.

**Simplified agent tools**
The LangChain tools make simple HTTP calls to the MCP Server instead of handling API keys, geocoding, and data parsing themselves.

**Easier testing**
Each layer can be tested in isolation — mock the MCP Server to test the agent, mock OpenWeatherMap to test the MCP Server.

**Reusability**
Any other service or frontend can consume the same MCP Server endpoints without needing the AI agent.

**Security**
The OpenWeatherMap API key lives only in the MCP Server. The agent backend and frontend never see it.

---

### Cons

**~~Added latency~~** *(mitigated)*
Every weather request goes through an extra network hop, but the LFU cache layer ensures repeated queries return instantly from memory (see the Improvements tab).

**Operational complexity**
There's an additional service to deploy, monitor, and maintain. A single-service setup would be simpler to run.

**~~Single point of failure~~** *(mitigated)*
The backend tools now include a direct fallback client — if the MCP Server is unreachable, they call OpenWeatherMap directly (see the Improvements tab).

**Overhead for simple use cases**
For an app with only one consumer (this agent), a separate microservice may be over-engineered compared to putting the API calls directly in the tools.

**Caching adds complexity**
An LFU cache layer has been added to reduce latency for repeated queries (see the Improvements tab), but it introduces additional state management and TTL considerations.
`;

export default function ArchitecturePanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{ARCHITECTURE_CONTENT}</Markdown>
    </div>
  );
}
