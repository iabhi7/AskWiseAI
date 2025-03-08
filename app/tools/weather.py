import httpx
from typing import Dict, Any
from app.tools.base import Tool
from config import settings

class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Get current weather information for a location"
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "location": {
                "type": "string",
                "description": "The city and optionally state/country"
            }
        }
    
    async def execute(self, location: str) -> Dict[str, Any]:
        """Get current weather for the specified location."""
        api_key = settings.WEATHER_API_KEY
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weatherapi.com/v1/current.json",
                params={
                    "key": api_key,
                    "q": location,
                    "aqi": "no"
                }
            )
            
            if response.status_code != 200:
                return {"error": f"Weather API error: {response.text}"}
            
            data = response.json()
            
            return {
                "location": f"{data['location']['name']}, {data['location']['country']}",
                "temperature_c": data['current']['temp_c'],
                "temperature_f": data['current']['temp_f'],
                "condition": data['current']['condition']['text'],
                "humidity": data['current']['humidity'],
                "wind_kph": data['current']['wind_kph']
            } 