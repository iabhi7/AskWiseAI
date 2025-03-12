import pytest
from unittest.mock import patch, AsyncMock
from app.router import route_query

@pytest.mark.asyncio
async def test_route_query_llm():
    # Mock the LLM response for routing decision
    with patch('app.router.get_llm_response', new_callable=AsyncMock) as mock_llm:
        # First call returns routing decision, second call returns the actual response
        mock_llm.side_effect = [
            {"use_tool": False, "reasoning": "This is general knowledge"},
            "Albert Einstein was a theoretical physicist born in 1879."
        ]
        
        result = await route_query("Who was Albert Einstein?")
        
        assert "tool_used" not in result
        assert "Albert Einstein" in result["response"]
        assert "reasoning" in result

@pytest.mark.asyncio
async def test_route_query_tool():
    # Mock the LLM response and tool execution
    with patch('app.router.get_llm_response', new_callable=AsyncMock) as mock_llm, \
         patch('app.tools.get_tool', new_callable=AsyncMock) as mock_get_tool:
        
        # Setup mock tool
        mock_tool = AsyncMock()
        mock_tool.execute.return_value = {
            "location": "New York, United States",
            "temperature_c": 22.5,
            "temperature_f": 72.5,
            "condition": "Partly cloudy",
            "humidity": 65,
            "wind_kph": 10.8,
            "last_updated": "2023-10-15 15:30"
        }
        mock_get_tool.return_value = mock_tool
        
        # Mock LLM responses
        mock_llm.side_effect = [
            {"use_tool": True, "tool_name": "weather", "tool_input": {"location": "New York"}, "reasoning": "Need real-time weather data"},
            "The current weather in New York is partly cloudy with a temperature of 22.5°C (72.5°F)."
        ]
        
        result = await route_query("What's the weather in New York?")
        
        assert result["tool_used"] == "weather"
        assert "New York" in result["response"]
        assert "temperature" in result["response"].lower()
        assert result["tool_input"] == {"location": "New York"} 