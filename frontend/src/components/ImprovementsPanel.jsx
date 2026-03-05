import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const IMPROVEMENTS_CONTENT = `
## Improvements

Optimizations and enhancements made to the Weather Agent system.

---

### LFU Cache Layer (MCP Server)

**Problem:** Every weather query made a round-trip to the OpenWeatherMap API, even for repeated requests for the same city. This added unnecessary latency and risked hitting API rate limits.

**Solution:** Added an in-memory LFU (Least Frequently Used) cache to the MCP Server's \`WeatherService\`. All four data-fetching methods — geocoding, current weather, forecast, and air quality — now check the cache before making external API calls.

#### How It Works

\`\`\`
Incoming Request (e.g., "current weather in Tokyo")
   |
   v
Generate cache key: "current:tokyo"
   |
   v
Cache HIT? ──── Yes ──> Return cached result instantly
   |
   No
   |
   v
Call OpenWeatherMap API
   |
   v
Store result in LFU cache (TTL: 5 min)
   |
   v
Return result
\`\`\`

#### LFU Eviction Policy

Unlike LRU (Least Recently Used), LFU tracks **how often** each entry is accessed, not just when it was last used. When the cache is full:

1. Find entries with the **lowest access frequency**
2. Among those, evict the **oldest** one (tie-breaker)
3. This keeps frequently queried cities (e.g., New York, London) in cache longer, even if there's a gap between requests

#### Cache Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Capacity | 128 entries | Max items before eviction kicks in |
| TTL | 300 seconds (5 min) | Ensures weather data stays reasonably fresh |
| Key format | \`{type}:{city}:{params}\` | Normalized (lowercased, trimmed) for deduplication |

#### What's Cached

| Cache Key Prefix | Method | Example Key |
|-----------------|--------|-------------|
| \`geo:\` | Geocoding (city → lat/lon) | \`geo:tokyo\` |
| \`current:\` | Current weather | \`current:new york\` |
| \`forecast:\` | Multi-day forecast | \`forecast:london:3\` |
| \`air:\` | Air quality index | \`air:paris\` |

#### Monitoring

A new endpoint \`GET /api/cache/stats\` exposes real-time cache metrics:

\`\`\`json
{
  "size": 12,
  "capacity": 128,
  "hits": 47,
  "misses": 15,
  "hit_rate": 0.758
}
\`\`\`

#### Impact

- **Repeated queries** for the same city return instantly from memory (sub-millisecond vs ~200-500ms API call)
- **Geocoding** is cached separately, so even cache misses on weather data avoid a redundant geocoding API call
- **Thread-safe** implementation using locks, safe for concurrent requests
- **Automatic expiry** ensures data never gets staler than 5 minutes

---

### Pluggable Weather Provider (MCP Server)

**Problem:** The MCP Server was tightly coupled to OpenWeatherMap. Every method in \`WeatherService\` directly constructed OpenWeatherMap URLs, parsed its response format, and used its API key. Switching to a different provider (e.g., WeatherAPI, Tomorrow.io, AccuWeather) would require rewriting the entire service.

**Solution:** Introduced a **provider abstraction** using the Strategy pattern. The weather service now delegates all API calls to a pluggable provider that implements a standard interface.

#### Architecture

\`\`\`
WeatherService (caching layer)
   |
   |  delegates to
   v
WeatherProvider (abstract interface)
   |
   ├── OpenWeatherMapProvider  (current)
   ├── WeatherAPIProvider      (add in future)
   └── TomorrowIOProvider      (add in future)
\`\`\`

#### How to Add a New Provider

1. Create a new file in \`mcp-server/services/providers/\` (e.g., \`weatherapi.py\`)
2. Implement the \`WeatherProvider\` abstract class with four methods:
   - \`geocode(city)\` → \`{lat, lon, name, country}\`
   - \`get_current_weather(city)\` → standardized current weather dict
   - \`get_forecast(city, days)\` → standardized forecast dict
   - \`get_air_quality(city)\` → standardized air quality dict
3. Register it in the factory function in \`main.py\`
4. Set \`WEATHER_PROVIDER=your_provider\` in \`.env\`

#### How to Switch Providers

Change one environment variable:

\`\`\`bash
# .env
WEATHER_PROVIDER=openweathermap   # current default
\`\`\`

No code changes required — the factory in \`main.py\` instantiates the correct provider at startup.

#### Key Design Decisions

- **Standardized response schema** — Every provider must return the same dict structure, so the cache, API endpoints, and agent tools all work unchanged
- **Cache stays in WeatherService** — The caching layer is provider-agnostic and wraps any provider automatically
- **Provider owns geocoding** — Different APIs handle city lookup differently, so each provider implements its own \`geocode()\` method
- **Factory pattern** — A single \`create_weather_service()\` function in \`main.py\` maps the config string to the concrete provider class

---

### Direct Fallback — Eliminating the Single Point of Failure

**Problem:** If the MCP Server went down, the entire weather functionality broke — even though the agent backend was healthy. The MCP Server was a single point of failure.

**Solution:** Added a \`DirectWeatherClient\` in the backend that calls OpenWeatherMap directly, bypassing the MCP Server. Each tool now tries the MCP Server first, and automatically falls back to the direct client on connection errors, timeouts, or 5xx server errors.

#### How It Works

\`\`\`
Tool receives request (e.g., get_current_weather("Tokyo"))
   |
   v
Try MCP Server (primary path)
   |
   ├── Success ──> Return result
   ├── 4xx error (e.g., city not found) ──> Return error (no fallback)
   └── Connection error / timeout / 5xx ──> Fall through
                                              |
                                              v
                                     Try DirectWeatherClient
                                              |
                                              ├── Success ──> Return result + [FALLBACK] marker
                                              └── Error ──> Return error message
\`\`\`

#### Key Decisions

- **Only fall back on infrastructure failures** — A 404 (city not found) is a legitimate response, not an MCP failure. Fallback only triggers on connection errors, timeouts, and 5xx errors.
- **Frontend shows "(fallback - MCP server unavailable)"** — Users see a yellow badge when the response came from the direct path, so it's transparent.
- **No caching on fallback** — The direct client doesn't have the LFU cache. This is intentional — it's a degraded mode, not a replacement.
- **Same response format** — The \`DirectWeatherClient\` returns the same dict schema as the MCP provider, so the LLM agent sees identical data regardless of the path.
- **\`OPENWEATHER_API_KEY\` shared** — The backend reads the same API key from \`.env\` that the MCP server uses.

---

### Unit Tests with Mocked Layers (66 tests)

**Problem:** No tests existed for any layer. Bugs could only be caught by running the full stack end-to-end, which requires live API keys and running services.

**Solution:** Added comprehensive unit tests for every layer, using mocks to isolate each layer from its dependencies. Each test suite targets one layer and simulates the layers below it.

#### Test Structure

\`\`\`
mcp-server/tests/
  test_lfu_cache.py           12 tests — pure unit tests, no mocks
  test_provider_openweathermap.py  7 tests — mocks httpx client
  test_weather_service.py      8 tests — mocks the provider
  test_api.py                 11 tests — mocks the weather service

backend/tests/
  test_direct_weather.py       5 tests — mocks httpx for direct client
  test_tools.py               10 tests — mocks MCP + fallback paths
  test_agent.py                6 tests — mocks the LangChain agent
  test_api.py                  7 tests — mocks run_agent
\`\`\`

#### What Each Layer Tests

| Test File | Layer Under Test | What's Mocked | Key Assertions |
|-----------|-----------------|---------------|----------------|
| \`test_lfu_cache\` | LFU Cache | Nothing (pure logic) | Eviction order, TTL expiry, hit/miss stats |
| \`test_provider_openweathermap\` | OpenWeatherMap Provider | \`httpx.AsyncClient\` | Response parsing, geocoding, error propagation |
| \`test_weather_service\` | WeatherService | WeatherProvider | Cache hits skip provider, case-insensitive keys |
| \`test_api\` (MCP) | FastAPI endpoints | WeatherService | HTTP status codes, error handling, param validation |
| \`test_direct_weather\` | DirectWeatherClient | \`httpx.get\` | Geocoding, response parsing, error handling |
| \`test_tools\` | LangChain tools | \`httpx.get\` + DirectWeatherClient | MCP path, fallback path, cached/fallback markers |
| \`test_agent\` | run_agent() | LangChain agent | Message construction, tool call extraction, cached/fallback flags |
| \`test_api\` (backend) | FastAPI endpoints | run_agent + get_agent | Request validation, error/fallback responses |

#### Running Tests

\`\`\`bash
# MCP Server (38 tests)
cd mcp-server && source venv/bin/activate && python -m pytest tests/ -v

# Backend (28 tests)
cd backend && source venv/bin/activate && python -m pytest tests/ -v
\`\`\`

---

### Security Hardening

**Problem:** The application needed a security review to ensure API keys stay private and the attack surface is minimized.

#### What Was Already Secure

- **API keys loaded from environment variables** — All secrets (\`OPENWEATHER_API_KEY\`, \`ANTHROPIC_API_KEY\`) are read via \`os.getenv()\` in \`config.py\` files, never hardcoded
- **\`.env\` excluded from version control** — Listed in \`.gitignore\`, never committed to git history
- **\`.env.example\` with placeholders** — Safe template for onboarding without exposing real keys

#### What Was Fixed

| Issue | Risk | Fix |
|-------|------|-----|
| CORS \`allow_origins=["*"]\` | Any website could make API requests to the backend | Restricted to \`ALLOWED_ORIGINS\` env var (defaults to localhost dev servers) |
| CORS \`allow_methods=["*"]\` | Unnecessary HTTP methods exposed | Restricted to \`GET, POST\` (backend) and \`GET\` (MCP server) |
| Error messages leaked internals | \`str(e)\` in 500 responses could expose stack traces, file paths, or config | Generic error messages for 500s; only \`ValueError\` (city not found) returns specific details |
| No input length limits | Oversized payloads could abuse the LLM or cause memory issues | Chat message capped at 1,000 chars; city name capped at 100 chars |

#### CORS Configuration

Origins are configurable via environment variable — no code change needed for deployment:

\`\`\`bash
# .env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
\`\`\`

#### Additional Security Recommendations

These are not yet implemented but would further harden the application for production:

- **Rate limiting** — Add request throttling (e.g., \`slowapi\`) to prevent abuse of the LLM endpoint, which is expensive per-call
- **HTTPS everywhere** — Use TLS termination (via reverse proxy like Nginx or cloud load balancer) for all traffic
- **API key rotation** — Periodically rotate \`OPENWEATHER_API_KEY\` and \`ANTHROPIC_API_KEY\`; update \`.env\` and restart services
- **Request size limits** — Configure max request body size at the reverse proxy level (e.g., 10KB)
- **Helmet-style headers** — Add security headers (\`X-Content-Type-Options\`, \`X-Frame-Options\`, \`Strict-Transport-Security\`) via middleware
- **Logging and monitoring** — Log failed requests and anomalous patterns without exposing sensitive data in logs
`;

export default function ImprovementsPanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{IMPROVEMENTS_CONTENT}</Markdown>
    </div>
  );
}
