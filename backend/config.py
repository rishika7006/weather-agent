import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. LLM agent will fail.")
