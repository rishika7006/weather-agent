from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from config import ANTHROPIC_API_KEY
from tools import ALL_TOOLS, CACHED_MARKER, FALLBACK_MARKER

SYSTEM_PROMPT = """You are a helpful weather assistant. You provide accurate, friendly, and
concise weather information to users.

You have access to three tools:
1. get_current_weather - Get real-time weather conditions for any city
2. get_weather_forecast - Get a multi-day forecast (up to 5 days) for any city
3. get_air_quality - Get the air quality index and pollutant levels for any city

Guidelines:
- Always use the appropriate tool(s) to answer weather-related questions.
- If a user asks about multiple cities, call the tool for each city.
- Provide temperatures in Fahrenheit.
- When giving forecasts, summarize the key trends (warming up, cooling down, rain expected, etc.).
- For air quality, explain what the AQI level means for daily activities.
- If a user asks a non-weather question, politely let them know you specialize in weather information.
- Be conversational and helpful in your responses.
"""


def create_weather_agent():
    """Create and return a LangChain weather agent with tool-calling capabilities."""
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=ANTHROPIC_API_KEY,
        temperature=0.3,
        max_tokens=1024,
    )

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return agent


async def run_agent(agent, message: str, chat_history: list = None) -> dict:
    """Run the agent with a user message and return the response.

    Args:
        agent: The LangChain agent executor.
        message: The user's message.
        chat_history: Optional list of previous messages for context.

    Returns:
        Dict with 'response' (text) and 'tool_calls' (list of tools invoked).
    """
    messages = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    result = await agent.ainvoke({"messages": messages})

    # Extract the final AI response and any tool calls
    response_text = ""
    tool_calls_made = []
    any_cached = False
    any_fallback = False

    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_made.append({
                    "tool": tc["name"],
                    "args": tc["args"],
                })
        if isinstance(msg, ToolMessage):
            content = msg.content or ""
            if CACHED_MARKER in content:
                any_cached = True
            if FALLBACK_MARKER in content:
                any_fallback = True
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            response_text = msg.content

    return {
        "response": response_text,
        "tool_calls": tool_calls_made,
        "cached": any_cached,
        "fallback": any_fallback,
    }
