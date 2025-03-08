import httpx
from typing import Dict, Any
import re
from app.tools.base import Tool
from config import settings
from app.cache import tool_cache

class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Get current weather information for a location. Use this for questions about current weather conditions."
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "location": {
                "type": "string",
                "description": "The city name and optionally state/country (e.g., 'New York', 'London, UK')"
            }
        }
    
    async def execute(self, location: str) -> Dict[str, Any]:
        """Get current weather for the specified location."""
        # Input validation
        if not location or not isinstance(location, str):
            return {"error": "Invalid location. Please provide a valid city name."}
        
        # Sanitize input - only allow alphanumeric chars, spaces, and commas
        sanitized_location = re.sub(r'[^\w\s,]', '', location)
        if sanitized_location != location:
            print(f"Sanitized location from '{location}' to '{sanitized_location}'")
        
        # Check cache first
        cache_key = f"weather:{sanitized_location}"
        cached_result = tool_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Proceed with API call
        api_key = settings.WEATHER_API_KEY
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.weatherapi.com/v1/current.json",
                    params={
                        "key": api_key,
                        "q": sanitized_location,
                        "aqi": "no"
                    },
                    timeout=10.0  # Add timeout
                )
                
                if response.status_code != 200:
                    error_msg = f"Weather API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg = f"Weather API error: {error_data['error']['message']}"
                    except:
                        pass
                    return {"error": error_msg}
                
                data = response.json()
                
                result = {
                    "location": f"{data['location']['name']}, {data['location']['country']}",
                    "temperature_c": data['current']['temp_c'],
                    "temperature_f": data['current']['temp_f'],
                    "condition": data['current']['condition']['text'],
                    "humidity": data['current']['humidity'],
                    "wind_kph": data['current']['wind_kph'],
                    "last_updated": data['current']['last_updated']
                }
                
                # Cache the result for 30 minutes (weather changes)
                tool_cache.set(cache_key, result, ttl=1800)
                
                return result
                
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to weather service: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error getting weather data: {str(e)}"} 