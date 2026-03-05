import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not set. LLM agent will fail.")
if not OPENWEATHER_API_KEY:
    print("WARNING: OPENWEATHER_API_KEY not set. Direct weather fallback will be unavailable.")
