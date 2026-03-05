import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from agent import run_agent


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.ainvoke = AsyncMock()
    return agent


class TestRunAgent:
    @pytest.mark.asyncio
    async def test_basic_response(self, mock_agent):
        mock_agent.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="What's the weather?"),
                AIMessage(content="It's sunny in Tokyo!"),
            ]
        }
        result = await run_agent(mock_agent, "What's the weather?")
        assert result["response"] == "It's sunny in Tokyo!"
        assert result["tool_calls"] == []
        assert result["cached"] is False
        assert result["fallback"] is False

    @pytest.mark.asyncio
    async def test_response_with_tool_calls(self, mock_agent):
        ai_with_tool = AIMessage(content="")
        ai_with_tool.tool_calls = [
            {"name": "get_current_weather", "args": {"city": "Tokyo"}}
        ]
        mock_agent.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="Weather in Tokyo?"),
                ai_with_tool,
                ToolMessage(content="72\u00b0F clear sky", tool_call_id="1"),
                AIMessage(content="The weather in Tokyo is 72\u00b0F and clear."),
            ]
        }
        result = await run_agent(mock_agent, "Weather in Tokyo?")
        assert result["response"] == "The weather in Tokyo is 72\u00b0F and clear."
        assert len(result["tool_calls"]) == 1
        assert result["cached"] is False
        assert result["fallback"] is False

    @pytest.mark.asyncio
    async def test_cached_flag_detected_from_tool_message(self, mock_agent):
        ai_with_tool = AIMessage(content="")
        ai_with_tool.tool_calls = [
            {"name": "get_current_weather", "args": {"city": "Tokyo"}}
        ]
        mock_agent.ainvoke.return_value = {
            "messages": [
                ai_with_tool,
                ToolMessage(content="72\u00b0F clear sky\n[CACHED]", tool_call_id="1"),
                AIMessage(content="Sunny!"),
            ]
        }
        result = await run_agent(mock_agent, "Weather in Tokyo?")
        assert result["cached"] is True
        assert result["fallback"] is False

    @pytest.mark.asyncio
    async def test_fallback_flag_detected_from_tool_message(self, mock_agent):
        ai_with_tool = AIMessage(content="")
        ai_with_tool.tool_calls = [
            {"name": "get_current_weather", "args": {"city": "Tokyo"}}
        ]
        mock_agent.ainvoke.return_value = {
            "messages": [
                ai_with_tool,
                ToolMessage(content="72\u00b0F clear sky\n[FALLBACK]", tool_call_id="1"),
                AIMessage(content="Sunny!"),
            ]
        }
        result = await run_agent(mock_agent, "Weather in Tokyo?")
        assert result["cached"] is False
        assert result["fallback"] is True

    @pytest.mark.asyncio
    async def test_with_chat_history(self, mock_agent):
        mock_agent.ainvoke.return_value = {
            "messages": [AIMessage(content="Still sunny!")]
        }
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        result = await run_agent(mock_agent, "And now?", chat_history=history)
        call_args = mock_agent.ainvoke.call_args[0][0]
        messages = call_args["messages"]
        assert len(messages) == 3
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert isinstance(messages[2], HumanMessage)

    @pytest.mark.asyncio
    async def test_empty_history(self, mock_agent):
        mock_agent.ainvoke.return_value = {
            "messages": [AIMessage(content="Hello!")]
        }
        result = await run_agent(mock_agent, "Hi", chat_history=[])
        call_args = mock_agent.ainvoke.call_args[0][0]
        assert len(call_args["messages"]) == 1
