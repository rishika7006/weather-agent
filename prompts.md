# Development Prompts

Complete prompt sequence used to build this project end-to-end using **Claude Code** (Agentic IDE). Each prompt is listed in the order it was executed, grouped by development phase, with the agent used and files produced.

**Agentic IDE:** Cursor IDE with Claude Code CLI integrated for agentic development
**LLM powering the agents:** Claude Opus 4.6 (via Claude Code CLI)
**Total agents used:** 5 specialized agents (see Agentic Dev tab in frontend)

---

## Phase 1: Project Initialization

**Agent:** Scaffold Agent

### Prompt 1 — Project Planning

```
I'm building a full-stack agentic web application. The stack is:
1. A public REST API (OpenWeatherMap — free tier, covers current weather, forecasts, and air quality)
2. An MCP Server wrapper (FastAPI microservice) for the API's core functions
3. An LLM Agent backend using LangChain with tool/function calling against the MCP Server
4. A React frontend to interact with the agent

Set up the project structure with three separate directories: mcp-server/, backend/, frontend/.
Create a .gitignore (exclude .env, venv/, __pycache__/, node_modules/), a .env.example with
placeholder keys, and a README.md with setup instructions for each service.
```

**Files created:**
- `.gitignore`
- `.env.example` — placeholder keys for `OPENWEATHER_API_KEY`, `ANTHROPIC_API_KEY`, `MCP_SERVER_URL`
- `README.md` — project overview, setup steps, architecture diagram, dependency list

---

## Phase 2: MCP Server — Public REST API Wrapper

**Agent:** Scaffold Agent

### Prompt 2 — MCP Server Core

```
Build the MCP Server as a FastAPI microservice in mcp-server/ that wraps the OpenWeatherMap API.

Requirements:
- Three endpoints: /api/weather/current, /api/weather/forecast, /api/weather/air-quality
- Each endpoint accepts a city name (string) and handles geocoding internally (city → lat/lon)
- Normalize raw OpenWeatherMap responses into clean, consistent JSON
- Aggregate the 3-hour forecast intervals into daily summaries (high/low temp, dominant condition)
- Return all temperatures in Fahrenheit and wind speeds in mph
- Load OPENWEATHER_API_KEY from environment variables via python-dotenv
- Use httpx for async HTTP calls
- Add a /health endpoint

Create config.py, main.py, services/weather_service.py, and requirements.txt.
```

**Files created:**
| File | Purpose |
|------|---------|
| `mcp-server/main.py` | FastAPI app with 3 weather endpoints + health check |
| `mcp-server/config.py` | Loads `OPENWEATHER_API_KEY` from `.env` via `dotenv` |
| `mcp-server/services/weather_service.py` | Geocoding, API calls, response normalization |
| `mcp-server/services/__init__.py` | Package init |
| `mcp-server/requirements.txt` | `fastapi`, `uvicorn`, `httpx`, `python-dotenv` |

**Key design decisions:**
- Geocoding abstraction — callers only provide city names, never coordinates
- Response normalization — raw API responses transformed to clean, consistent JSON
- Forecast aggregation — 3-hour intervals grouped by day with high/low temps
- Imperial units by default

---

## Phase 3: LLM Agent Backend — Tool Calling

**Agent:** Scaffold Agent

### Prompt 3 — Agent Backend with LangChain

```
Build the LLM Agent backend in backend/ using LangChain and LangGraph.

Requirements:
- Use Anthropic Claude (claude-sonnet-4-20250514) via langchain-anthropic
- Create a ReAct agent using langgraph's create_react_agent
- Define three @tool functions: get_current_weather(city), get_weather_forecast(city, days),
  get_air_quality(city) — each calls the MCP Server endpoints via httpx
- Write a system prompt that instructs the agent to: use appropriate tools for weather queries,
  provide temperatures in Fahrenheit, summarize forecast trends, explain AQI levels,
  and politely decline non-weather questions
- FastAPI app with POST /api/chat endpoint accepting {message, chat_history}
- Lazy agent initialization (create on first request, not at import time)
- Load ANTHROPIC_API_KEY and MCP_SERVER_URL from environment variables
- Add a /health endpoint

Create agent.py, tools.py, main.py, config.py, and requirements.txt.
```

**Files created:**
| File | Purpose |
|------|---------|
| `backend/agent.py` | `create_weather_agent()` with Claude + ReAct pattern, `run_agent()` for message processing |
| `backend/tools.py` | Three `@tool` functions with docstrings (used by LLM for tool selection) |
| `backend/main.py` | FastAPI app with `/api/chat` endpoint, lazy agent init |
| `backend/config.py` | Loads `ANTHROPIC_API_KEY`, `MCP_SERVER_URL` from `.env` |
| `backend/requirements.txt` | `langchain-anthropic`, `langgraph`, `fastapi`, `uvicorn`, `httpx` |

**Tool calling architecture:**
- Each tool is a LangChain `@tool` with descriptive docstrings the LLM uses to decide invocation
- Tools make HTTP calls to MCP Server endpoints and format responses into readable strings
- The ReAct agent loop: reason → select tool → call tool → observe result → respond
- System prompt guides behavior (units, multi-city handling, AQI explanations)

---

## Phase 4: Frontend Web App

**Agent:** Scaffold Agent

### Prompt 4 — React Chat Interface

```
Build a React frontend in frontend/ using Vite.

Requirements:
- Chat interface with user/assistant message bubbles
- Input form with send button, disabled while loading
- Suggestion chips for common queries ("What's the weather in New York?", etc.)
- Show which tools the agent called below each response (e.g., "get_current_weather(Tokyo)")
- Loading animation while waiting for the agent
- Error handling with user-friendly messages
- Dark theme with modern, minimalistic styling
- Vite proxy config: /api requests → localhost:8000
- Render agent responses as Markdown (tables, code blocks, lists) using react-markdown + remark-gfm
- Auto-scroll to latest message

Create App.jsx, App.css, components/ChatInterface.jsx, components/MessageBubble.jsx,
vite.config.js, and package.json.
```

**Files created:**
| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Root component with tab navigation |
| `frontend/src/App.css` | Dark theme, responsive layout, message styling |
| `frontend/src/components/ChatInterface.jsx` | Chat UI: messages, input, suggestions, loading, errors |
| `frontend/src/components/MessageBubble.jsx` | User/assistant bubbles with Markdown rendering and tool badges |
| `frontend/src/main.jsx` | React entry point |
| `frontend/index.html` | HTML shell |
| `frontend/vite.config.js` | Vite config with API proxy to backend |
| `frontend/package.json` | `react`, `react-markdown`, `remark-gfm`, `vite` |
| `frontend/src/index.css` | Base styles |

---

## Phase 5: Frontend Documentation Tabs

**Agent:** Scaffold Agent

### Prompt 5 — Help Tab (API Documentation)

```
Create a Help tab on the frontend that documents the weather API capabilities for end users.
Show the three features they can use (current weather, forecast, air quality) with example
queries and what information each one returns. Keep it user-friendly, not technical.
```

**Files created:** `frontend/src/components/HelpPanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Help tab

### Prompt 6 — Architecture Tab

```
Create an Architecture tab showing the MCP Server architecture with:
- An ASCII diagram of the full request flow (User → Frontend → Agent → MCP Server → OpenWeatherMap)
- A table of the three endpoints and their purpose
- Key design decisions (geocoding abstraction, response normalization, forecast aggregation, imperial units)
- Pros (separation of concerns, independent scalability, simplified tools, easier testing, reusability, security)
- Cons (added latency, operational complexity, single point of failure, overhead for simple use cases)
```

**Files created:** `frontend/src/components/ArchitecturePanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Architecture tab

### Prompt 7 — Agent Tab (LLM & Tool Calling)

```
Create an Agent tab explaining the LLM Agent setup:
- The ReAct agent loop (reason → act → observe)
- Tool definitions with their signatures and what each one does
- The system prompt and why each guideline exists
- LangChain/LangGraph architecture (create_react_agent, ChatAnthropic, tool calling flow)
- How the agent decides which tool(s) to call
```

**Files created:** `frontend/src/components/AgentPanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Agent tab

### Prompt 8 — Experience Tab (End-to-End UX)

```
Create an Experience tab documenting the end-to-end user experience:
- The query flow from typing a question to seeing the response
- Suggestion chips for onboarding
- Loading states and error handling
- Markdown rendering of agent responses
- Tool call visibility (showing which tools the agent used)
```

**Files created:** `frontend/src/components/ExperiencePanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Experience tab

### Prompt 9 — Deployment Tab

```
Create a Deployment tab with a verbal overview of how the solution would be deployed:
- Docker Compose setup for all three services
- Kubernetes architecture with separate deployments
- Environment variable configuration for production
- Scaling strategy (horizontal scaling for MCP Server, single replica for agent backend)
- Serverless alternative (AWS Lambda for MCP, ECS for agent backend)
```

**Files created:** `frontend/src/components/DeploymentPanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Deployment tab

---

## Phase 6: Project Documentation

**Agent:** Admin Agent

### Prompt 10 — Agent Instructions File

```
Create an agents.md file for this project. Include:
- Project overview with the three-layer architecture
- Frontend tab structure (which component maps to which tab)
- A rule that every improvement or code change must be reflected in the relevant frontend tab
- A checklist mapping change types to the correct tab to update
```

**Files created:** `agents.md`

### Prompt 11 — Documentation Philosophy

```
Add a documentation philosophy section to agents.md with these principles:
1. Document every change — no change is too small to skip
2. Document the reason, not just the what — future developers need historical context
3. Comment exceptions and non-obvious code — so they aren't removed by mistake
4. Frontend tabs are the living documentation — the single source of truth for any new developer
```

**Files modified:** `agents.md`

---

## Phase 7: Improvements — Performance & Reliability

**Agent:** Optimizer Agent

### Prompt 12 — LFU Cache Layer

```
Add an LFU (Least Frequently Used) cache to the MCP Server's WeatherService to reduce latency
for repeated queries.

Requirements:
- In-memory cache with 128 entry capacity and 5-minute TTL
- LFU eviction: track access frequency per key, evict least-frequent (oldest as tie-breaker)
- Thread-safe with threading.Lock
- Cache all four methods: geocoding, current weather, forecast, air quality
- Normalized cache keys (lowercased, trimmed) for deduplication
- Add GET /api/cache/stats endpoint exposing size, capacity, hits, misses, hit_rate
- Return a cached flag in API responses so downstream consumers know the data came from cache

Create services/lfu_cache.py. Modify weather_service.py and main.py.
```

**Files created:** `mcp-server/services/lfu_cache.py`
**Files modified:** `mcp-server/services/weather_service.py`, `mcp-server/main.py`, `mcp-server/config.py`

### Prompt 13 — Improvements Tab

```
Create an Improvements tab on the frontend to document all optimizations made to the system.
Start with the LFU cache improvement — include the problem, solution, how it works (with a
flowchart), LFU eviction policy explanation, cache configuration table, what's cached, monitoring
endpoint, and impact.
```

**Files created:** `frontend/src/components/ImprovementsPanel.jsx`
**Files modified:** `frontend/src/App.jsx`

### Prompt 14 — Pluggable Weather Providers

```
Make the weather API provider pluggable using the Strategy pattern.

Requirements:
- Create an abstract WeatherProvider base class with four methods: geocode, get_current_weather,
  get_forecast, get_air_quality
- Extract the current OpenWeatherMap logic into an OpenWeatherMapProvider concrete class
- Make WeatherService a thin caching wrapper that accepts any WeatherProvider
- Add a factory function in main.py that reads WEATHER_PROVIDER from .env and instantiates
  the correct provider
- Switching providers should require zero code changes — just change the env var

Create services/providers/base.py, services/providers/openweathermap.py.
Update weather_service.py and main.py. Document in the Improvements tab.
```

**Files created:** `mcp-server/services/providers/base.py`, `mcp-server/services/providers/openweathermap.py`, `mcp-server/services/providers/__init__.py`
**Files modified:** `mcp-server/services/weather_service.py`, `mcp-server/main.py`, `mcp-server/config.py`
**Updated:** `ImprovementsPanel.jsx`, `ArchitecturePanel.jsx`

### Prompt 15 — Unit Tests with Mocked Layers

```
Add comprehensive unit tests for every layer, using mocks to isolate each layer from its
dependencies.

Test structure:
- mcp-server/tests/test_lfu_cache.py — pure unit tests for cache logic (eviction, TTL, stats)
- mcp-server/tests/test_provider_openweathermap.py — mock httpx.AsyncClient
- mcp-server/tests/test_weather_service.py — mock the WeatherProvider
- mcp-server/tests/test_api.py — mock the WeatherService
- backend/tests/test_direct_weather.py — mock httpx.get
- backend/tests/test_tools.py — mock MCP server + fallback paths
- backend/tests/test_agent.py — mock the LangChain agent
- backend/tests/test_api.py — mock run_agent

Use pytest with unittest.mock (AsyncMock, MagicMock, patch). Each test file should be
self-contained with its own fixtures and mock data. Target: full coverage of happy paths,
error paths, and edge cases.
```

**Files created (66 tests total):**
| File | Tests | Layer Tested | What's Mocked |
|------|-------|-------------|---------------|
| `mcp-server/tests/test_lfu_cache.py` | 12 | LFU Cache | Nothing (pure logic) |
| `mcp-server/tests/test_provider_openweathermap.py` | 7 | OpenWeatherMap Provider | `httpx.AsyncClient` |
| `mcp-server/tests/test_weather_service.py` | 8 | WeatherService | WeatherProvider |
| `mcp-server/tests/test_api.py` | 11 | FastAPI endpoints | WeatherService |
| `backend/tests/test_direct_weather.py` | 5 | DirectWeatherClient | `httpx.get` |
| `backend/tests/test_tools.py` | 10 | LangChain tools | `httpx.get` + DirectWeatherClient |
| `backend/tests/test_agent.py` | 6 | `run_agent()` | LangChain agent |
| `backend/tests/test_api.py` | 7 | FastAPI endpoints | `run_agent` + `get_agent` |

**Updated:** `ImprovementsPanel.jsx`

### Prompt 16 — Cached Response Badge in Frontend

```
When the MCP Server returns a cached response, show a "(cached)" badge below that message
in the frontend.

The challenge: the LLM sits between the tool output and the frontend, so it rewrites everything.
Solution: append a [CACHED] marker string to the tool output, detect it in run_agent() by
scanning ToolMessage content, and pass a cached boolean flag through the API response to the
frontend. Display it as a cyan badge below the message.
```

**Files modified:** `backend/tools.py`, `backend/agent.py`, `backend/main.py`, `frontend/src/components/MessageBubble.jsx`, `frontend/src/components/ChatInterface.jsx`, `frontend/src/App.css`

### Prompt 17 — Direct Fallback (Eliminate Single Point of Failure)

```
The MCP Server is a single point of failure — if it goes down, all weather functionality breaks.
Add a direct fallback.

Requirements:
- Create a DirectWeatherClient in the backend that calls OpenWeatherMap directly (bypassing MCP)
- Each tool should try MCP first, then fall back to direct client on connection errors, timeouts,
  or 5xx server errors
- Do NOT fall back on 4xx errors (e.g., city not found) — those are legitimate responses
- Show a "(fallback - MCP server unavailable)" amber badge in the frontend when fallback is used
- DirectWeatherClient must return the same response schema as the MCP provider
- Use the same OPENWEATHER_API_KEY from .env

Create backend/direct_weather.py. Update tools.py, agent.py, config.py.
Document in the Improvements tab. Update Architecture tab to mark single-point-of-failure
as mitigated.
```

**Files created:** `backend/direct_weather.py`
**Files modified:** `backend/tools.py`, `backend/agent.py`, `backend/config.py`, `frontend/src/components/MessageBubble.jsx`, `frontend/src/App.css`
**Updated:** `ImprovementsPanel.jsx`, `ArchitecturePanel.jsx`

### Prompt 18 — Security Hardening

```
Harden the application security:

1. Verify: API keys are loaded from env variables (not hardcoded), .env is in .gitignore and
   never committed, .env.example has safe placeholders
2. Fix: Restrict CORS from allow_origins=["*"] to a configurable ALLOWED_ORIGINS env var
   (default to localhost dev servers). Restrict allow_methods to only needed HTTP verbs.
3. Fix: Sanitize error messages — return generic messages for 500 errors instead of str(e)
   which can leak internal details (stack traces, file paths, config)
4. Fix: Add input length validation — cap chat messages at 1000 chars, city names at 100 chars
5. Suggest: Additional security improvements for production (rate limiting, HTTPS, API key
   rotation, request size limits, security headers)

Update both backend/main.py and mcp-server/main.py. Document in the Improvements tab.
```

**Files modified:** `backend/main.py`, `mcp-server/main.py`, `.env.example`
**Updated:** `ImprovementsPanel.jsx`

### Prompt 19 — Mitigate Architecture Cons

```
Update the Architecture tab: for all cons that have been addressed by improvements, show them
as mitigated (strikethrough with a note pointing to the Improvements tab). Specifically:
- "Added latency" → mitigated by LFU cache
- "Single point of failure" → mitigated by direct fallback
Leave unaddressed cons as-is.
```

**Files modified:** `frontend/src/components/ArchitecturePanel.jsx`

---

## Phase 8: Frontend Optimization

**Agent:** Interface Agent

### Prompt 20 — Responsive & Minimalist Design

```
Optimize the frontend for all screen sizes and keep it minimalist:
- Responsive breakpoints for mobile, tablet, and desktop
- Streamlined tab layout that doesn't overflow on small screens
- Accessible contrast ratios in the dark theme
- Minimalistic — no unnecessary chrome, content-first layout
- Clean spacing and typography
```

**Files modified:** `frontend/src/App.css`, `frontend/src/App.jsx`

---

## Phase 9: Version Control & GitHub

**Agent:** Pipeline Agent

### Prompt 21 — GitHub Repository Setup

```
Set up GitHub CLI, create a new repository, and push all project code.

Requirements:
- Clean commit history with each commit scoped to a logical unit of work
- Ensure .env is excluded and never committed (verify with git log)
- .env.example is committed with placeholder values
- Meaningful commit messages that describe the "why" not just the "what"
- Push to main branch
```

**Commits pushed (chronological):**
1. `803821f` — Initial commit: add `.gitignore`
2. `aced4b8` — Add project README and environment template
3. `d27e029` — Add MCP Server: FastAPI wrapper for OpenWeatherMap API
4. `084d152` — Add LLM Agent Backend: LangChain agent with tool calling
5. `a86ce33` — Add React Frontend: chat interface with weather agent
6. `4bf6001` — Fix agent backend: lazy LLM initialization
7. `1da058a` — Switch LLM from OpenAI to Anthropic Claude and fix config loading
8. `149b656` — Add markdown rendering for agent responses
9. `4236dd5` — Add multi-provider weather service, LFU cache, frontend panels, and tests

---

## Phase 10: Agentic Development Documentation

**Agent:** Optimizer Agent

### Prompt 22 — Agentic Dev Tab

```
Create an "Agentic Dev" tab on the frontend documenting the five agents used to build this
project. For each agent, describe its role, what it built, key decisions it made, and design
patterns used. Give each agent a technical name:
- Agent 1 (Scaffold Agent): base code — API selection, MCP Server, LLM agent, frontend
- Agent 2 (Optimizer Agent): all improvements — cache, providers, fallback, tests, security
- Agent 3 (Admin Agent): documentation — agents.md, documentation philosophy
- Agent 4 (Interface Agent): frontend optimization — responsive, minimalist
- Agent 5 (Pipeline Agent): GitHub — CLI setup, repo creation, push, commit history
```

**Files created:** `frontend/src/components/AgenticDevPanel.jsx`
**Files modified:** `frontend/src/App.jsx` — added Agentic Dev tab

### Prompt 23 — Prompts Documentation

```
Create a prompts.md file documenting all prompts used to build this project in chronological
order, grouped by phase. For each prompt include: the exact prompt text, which agent was used,
files created/modified, and key design decisions made. Map to evaluation criteria at the end.
```

**Files created:** `prompts.md` — this file

---

## Summary

| Phase | Agent | Prompts | Key Deliverable |
|-------|-------|---------|-----------------|
| 1. Project Setup | Scaffold Agent | 1 | `.gitignore`, `.env.example`, `README.md` |
| 2. MCP Server | Scaffold Agent | 2 | FastAPI wrapper for OpenWeatherMap (3 endpoints) |
| 3. LLM Agent Backend | Scaffold Agent | 3 | LangChain ReAct agent with 3 tools |
| 4. Frontend Web App | Scaffold Agent | 4 | React chat UI with dark theme |
| 5. Documentation Tabs | Scaffold Agent | 5–9 | Help, Architecture, Agent, Experience, Deployment panels |
| 6. Project Docs | Admin Agent | 10–11 | `agents.md` with documentation philosophy |
| 7. Improvements | Optimizer Agent | 12–19 | LFU cache, pluggable providers, fallback, 66 tests, security |
| 8. Frontend Polish | Interface Agent | 20 | Responsive, minimalist design |
| 9. GitHub | Pipeline Agent | 21 | Repository with clean commit history |
| 10. Agentic Dev Docs | Optimizer Agent | 22–23 | Agent documentation and prompt history |

**Total prompts:** 23
**Total files in project:** 50+
**Total unit tests:** 66
**Agents used:** 5

---

## Evaluation Criteria Mapping

| Category (Weight) | How This Project Addresses It |
|--------------------|-------------------------------|
| **Agentic Development (30%)** | 5 specialized agents with distinct scopes; 23 well-structured prompts; iterative improvement workflow; each prompt is specific, actionable, and demonstrates prompt engineering skill |
| **Architectural Design (30%)** | MCP Server with separation of concerns; Strategy pattern for pluggable providers; LFU cache with cache-aside pattern; direct fallback eliminating single point of failure; CORS restriction; env-based secrets; input validation; 66 unit tests |
| **LLM & Tooling (20%)** | LangChain/LangGraph ReAct agent; 3 tool definitions with descriptive docstrings; system prompt engineering for weather context; marker-based metadata propagation (`[CACHED]`, `[FALLBACK]`) through the LLM boundary |
| **Presentation & Documentation (20%)** | 7 frontend tabs as living documentation; `agents.md` with documentation philosophy; `README.md` with setup instructions; `prompts.md` with full development history; clean Git commit history; deployment discussion with Docker/K8s/Serverless |
