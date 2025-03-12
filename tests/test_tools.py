import pytest
from unittest.mock import patch, AsyncMock
from app.tools.weather import WeatherTool
from app.tools.stocks import StocksTool

@pytest.mark.asyncio
async def test_weather_tool():
    weather_tool = WeatherTool()
    
    # Test with mocked API response
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "location": {
                "name": "London",
                "country": "United Kingdom"
            },
            "current": {
                "temp_c": 15.0,
                "temp_f": 59.0,
                "condition": {
                    "text": "Partly cloudy"
                },
                "humidity": 76,
                "wind_kph": 11.2,
                "last_updated": "2023-10-15 14:30"
            }
        }
        mock_get.return_value = mock_response
        
        result = await weather_tool.execute(location="London")
        
        assert result["location"] == "London, United Kingdom"
        assert result["temperature_c"] == 15.0
        assert result["condition"] == "Partly cloudy"

@pytest.mark.asyncio
async def test_stocks_tool():
    stocks_tool = StocksTool()
    
    # Test with mocked API response
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Global Quote": {
                "01. symbol": "AAPL",
                "05. price": "178.72",
                "09. change": "1.45",
                "10. change percent": "0.82%",
                "06. volume": "48300000",
                "07. latest trading day": "2023-10-15"
            }
        }
        mock_get.return_value = mock_response
        
        result = await stocks_tool.execute(ticker="AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["price"] == "178.72"
        assert result["change"] == "1.45" 