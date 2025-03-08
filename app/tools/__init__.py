from typing import Dict, Optional
from app.tools.base import Tool
from app.tools.weather import WeatherTool
from app.tools.stocks import StocksTool

# Registry of available tools
_TOOLS: Dict[str, Tool] = {
    "weather": WeatherTool(),
    "stocks": StocksTool()
}

def get_tool(name: str) -> Optional[Tool]:
    """Get a tool by name."""
    return _TOOLS.get(name)

def list_tools() -> Dict[str, Dict]:
    """List all available tools with their descriptions and parameters."""
    return {
        name: {
            "description": tool.description,
            "parameters": tool.parameters
        }
        for name, tool in _TOOLS.items()
    } 