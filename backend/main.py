from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import create_weather_agent, run_agent

app = FastAPI(
    title="Weather Agent Backend",
    description="LLM-powered weather agent using LangChain with tool calling",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy agent initialization (created on first request so the server can start without keys)
_weather_agent = None


def get_agent():
    global _weather_agent
    if _weather_agent is None:
        _weather_agent = create_weather_agent()
    return _weather_agent


class ChatRequest(BaseModel):
    message: str
    chat_history: list = []


class ChatResponse(BaseModel):
    response: str
    tool_calls: list = []


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-backend"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the weather agent and get a response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        agent = get_agent()
        result = await run_agent(agent, request.message, request.chat_history)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
