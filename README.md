# Weather Agent - Agentic Web App with API Wrapper

A full-stack, agent-driven weather application that uses an LLM (via LangChain) with tool-calling capabilities to fetch and present weather data through a microservice architecture.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  React       │────▶│  LLM Agent       │────▶│  MCP Server     │────▶│  OpenWeatherMap  │
│  Frontend    │◀────│  Backend         │◀────│  (FastAPI)      │◀────│  API             │
│  (Vite)      │     │  (FastAPI +      │     │  Port 8001      │     │                  │
│  Port 5173   │     │   LangChain)     │     │                 │     │                  │
│              │     │  Port 8000       │     │                 │     │                  │
└──────────────┘     └──────────────────┘     └─────────────────┘     └──────────────────┘
```

**User** → types a natural-language query (e.g., "What's the weather in Tokyo?")
→ **React Frontend** sends it to the **Agent Backend**
→ **LangChain Agent** decides which tool(s) to call
→ Tools make HTTP requests to the **MCP Server**
→ **MCP Server** calls the **OpenWeatherMap API** and normalizes the response
→ Agent synthesizes a human-friendly answer → displayed in the **Frontend**

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite |
| Agent Backend | Python, FastAPI, LangChain, LangGraph |
| MCP Server | Python, FastAPI, httpx |
| LLM | Anthropic Claude (claude-sonnet-4-20250514) |
| External API | OpenWeatherMap (Current Weather, 5-Day Forecast, Air Pollution) |

## Project Structure

```
├── mcp-server/                    # MCP Server - OpenWeatherMap API wrapper
│   ├── main.py                    # FastAPI endpoints
│   ├── config.py                  # Environment configuration
│   ├── requirements.txt
│   ├── services/
│   │   ├── weather_service.py     # Weather service with caching
│   │   ├── lfu_cache.py           # LFU cache implementation
│   │   └── providers/
│   │       ├── base.py            # Abstract weather provider
│   │       └── openweathermap.py  # OpenWeatherMap provider
│   └── tests/                     # MCP Server test suite
├── backend/                       # LLM Agent Backend
│   ├── main.py                    # FastAPI chat endpoint
│   ├── agent.py                   # LangChain agent with tool calling
│   ├── tools.py                   # Tool definitions (calls MCP Server)
│   ├── direct_weather.py          # Direct weather utility
│   ├── config.py                  # Environment configuration
│   ├── requirements.txt
│   └── tests/                     # Backend test suite
├── frontend/                      # React Frontend
│   ├── src/
│   │   ├── App.jsx                # Root component with tab navigation
│   │   ├── App.css                # Styles
│   │   └── components/
│   │       ├── ChatInterface.jsx  # Chat container
│   │       ├── MessageBubble.jsx  # Message display with markdown
│   │       ├── AgentPanel.jsx     # Agent architecture panel
│   │       ├── ArchitecturePanel.jsx
│   │       ├── DeploymentPanel.jsx
│   │       ├── ExperiencePanel.jsx
│   │       ├── HelpPanel.jsx
│   │       └── ImprovementsPanel.jsx
│   ├── vite.config.js             # Vite config with API proxy
│   └── package.json
├── .env.example                   # Environment variable template
├── agents.md                      # Agent design documentation
└── README.md
```

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **OpenWeatherMap API Key** (free tier)
- **Anthropic API Key**

## Setup & Running

### 1. Clone and Configure Environment

```bash
git clone <repository-url>
cd InMarket_Challenge_Project

# Copy the environment template and add your API keys
cp .env.example .env
```

Edit `.env` and add your API keys:
- **OpenWeatherMap**: Sign up at [openweathermap.org](https://openweathermap.org/api) → API Keys section (free tier)
- **Anthropic**: Get a key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

### 2. Start the MCP Server (Port 8001)

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Verify: `curl http://localhost:8001/health`

### 3. Start the Agent Backend (Port 8000)

Open a new terminal:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Verify: `curl http://localhost:8000/health`

### 4. Start the Frontend (Port 5173)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

## Usage

Type natural-language weather queries in the chat interface:

- "What's the weather in New York?"
- "Give me a 5-day forecast for Tokyo"
- "How's the air quality in Los Angeles?"
- "Compare the weather in London and Paris"

The agent will automatically select the appropriate tool(s), fetch data via the MCP Server, and return a conversational response.

## API Endpoints

### MCP Server (Port 8001)

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/weather/current?city={city}` | Current weather |
| `GET /api/weather/forecast?city={city}&days={n}` | Multi-day forecast (1-5 days) |
| `GET /api/weather/air-quality?city={city}` | Air quality index |

### Agent Backend (Port 8000)

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `POST /api/chat` | Send a message to the weather agent |

## Key Design Decisions

- **Separation of Concerns**: The MCP Server handles all external API communication, while the Agent Backend focuses on LLM orchestration. This makes each service independently testable and deployable.
- **Tool Calling via LangChain**: The agent uses LangGraph's `create_react_agent` with Anthropic Claude's tool calling to decide which weather tools to invoke based on the user's query.
- **API Key Security**: All secrets are loaded from environment variables via `.env`, never hardcoded or committed to version control.
- **Vite Proxy**: The frontend proxies `/api` requests to the backend, avoiding CORS issues in development.

## Deployment Considerations

- **Docker**: Each service (MCP Server, Backend, Frontend) can be containerized with its own Dockerfile and orchestrated via `docker-compose`.
- **Kubernetes**: For production scale, deploy as separate pods with service discovery. The MCP Server and Backend would be internal services; the Frontend served via an ingress.
- **Serverless**: The MCP Server and Agent Backend are stateless and could run as AWS Lambda functions behind API Gateway, with the React frontend on CloudFront/S3.
