import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    WEATHER_API_KEY: str = os.environ.get("WEATHER_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
    
    # LLM Settings
    DEFAULT_MODEL: str = "gpt-4"
    
    class Config:
        env_file = ".env"

settings = Settings() 