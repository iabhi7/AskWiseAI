import httpx
from typing import Dict, Any
from app.tools.base import Tool
from config import settings

class StocksTool(Tool):
    @property
    def name(self) -> str:
        return "stocks"
    
    @property
    def description(self) -> str:
        return "Get current stock price information"
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ticker": {
                "type": "string",
                "description": "The stock ticker symbol (e.g., AAPL, MSFT)"
            }
        }
    
    async def execute(self, ticker: str) -> Dict[str, Any]:
        """Get current stock price for the specified ticker."""
        api_key = settings.ALPHA_VANTAGE_API_KEY
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": ticker,
                    "apikey": api_key
                }
            )
            
            if response.status_code != 200:
                return {"error": f"Stock API error: {response.text}"}
            
            data = response.json()
            
            if "Global Quote" not in data or not data["Global Quote"]:
                return {"error": f"No data found for ticker {ticker}"}
            
            quote = data["Global Quote"]
            
            return {
                "ticker": ticker.upper(),
                "price": quote.get("05. price", "N/A"),
                "change": quote.get("09. change", "N/A"),
                "change_percent": quote.get("10. change percent", "N/A"),
                "volume": quote.get("06. volume", "N/A"),
                "latest_trading_day": quote.get("07. latest trading day", "N/A")
            } 