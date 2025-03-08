import httpx
from typing import Dict, Any
import re
from app.tools.base import Tool
from config import settings
from app.cache import tool_cache

class StocksTool(Tool):
    @property
    def name(self) -> str:
        return "stocks"
    
    @property
    def description(self) -> str:
        return "Get current stock price information. Use this for questions about current stock prices, market data, or company ticker information."
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ticker": {
                "type": "string",
                "description": "The stock ticker symbol (e.g., 'AAPL' for Apple, 'MSFT' for Microsoft, 'GOOG' for Google)"
            }
        }
    
    async def execute(self, ticker: str) -> Dict[str, Any]:
        """Get current stock price for the specified ticker."""
        # Input validation
        if not ticker or not isinstance(ticker, str):
            return {"error": "Invalid ticker symbol. Please provide a valid stock ticker."}
        
        # Sanitize input - only allow alphanumeric chars
        sanitized_ticker = re.sub(r'[^\w]', '', ticker).upper()
        if sanitized_ticker != ticker.upper():
            print(f"Sanitized ticker from '{ticker}' to '{sanitized_ticker}'")
        
        # Check cache first
        cache_key = f"stocks:{sanitized_ticker}"
        cached_result = tool_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Proceed with API call
        api_key = settings.ALPHA_VANTAGE_API_KEY
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.alphavantage.co/query",
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": sanitized_ticker,
                        "apikey": api_key
                    },
                    timeout=10.0  # Add timeout
                )
                
                if response.status_code != 200:
                    return {"error": f"Stock API error: {response.status_code}"}
                
                data = response.json()
                
                if "Global Quote" not in data or not data["Global Quote"]:
                    return {"error": f"No data found for ticker {sanitized_ticker}. Please check if the ticker symbol is correct."}
                
                quote = data["Global Quote"]
                
                result = {
                    "ticker": sanitized_ticker,
                    "price": quote.get("05. price", "N/A"),
                    "change": quote.get("09. change", "N/A"),
                    "change_percent": quote.get("10. change percent", "N/A"),
                    "volume": quote.get("06. volume", "N/A"),
                    "latest_trading_day": quote.get("07. latest trading day", "N/A")
                }
                
                # Cache the result for 5 minutes (stock prices change frequently)
                tool_cache.set(cache_key, result, ttl=300)
                
                return result
                
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to stock service: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error getting stock data: {str(e)}"} 