import os
import json
from typing import Dict, Any, Optional
import httpx
from config import settings

async def get_llm_response(
    prompt: str, 
    model: str = settings.DEFAULT_MODEL,
    temperature: float = 0.7,
    response_format: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get a response from the LLM.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use
        temperature: The temperature parameter for generation
        response_format: Optional format specification (for JSON responses)
        
    Returns:
        The LLM's response as a string
    """
    # This example uses OpenAI's API, but could be adapted for other providers
    api_key = settings.OPENAI_API_KEY
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    
    if response_format:
        payload["response_format"] = response_format
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.text}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # If expecting JSON, parse it
        if response_format and response_format.get("type") == "json_object":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse JSON from LLM response: {content}")
        
        return content 