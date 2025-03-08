from typing import Dict, Any
import re
from app.llm_service import get_llm_response
from app.tools import get_tool

# Routing prompt to help LLM decide whether to use a tool
ROUTING_PROMPT = """
You are an AI assistant that can answer questions directly or use tools when necessary.
Given the user query, determine if you should:
1. Answer directly using your knowledge (for general information, opinions, etc.)
2. Use a tool to get real-time or specialized information

Available tools:
- weather: Get current weather for a location. Use for current weather questions.
- stocks: Get current stock price. Use for current stock price questions.

Respond with JSON in this format:
{
  "use_tool": true/false,
  "tool_name": "weather" or "stocks" (if use_tool is true),
  "tool_input": {key-value parameters for the tool} (if use_tool is true),
  "reasoning": "Brief explanation of your decision"
}

User query: {query}
"""

async def route_query(query: str) -> Dict[str, Any]:
    """
    Route the query to either the LLM or an appropriate tool
    """
    # Ask LLM to decide whether to use a tool
    routing_decision = await get_llm_response(
        ROUTING_PROMPT.format(query=query),
        response_format={"type": "json_object"}
    )
    
    # Parse the routing decision
    try:
        decision = routing_decision
        
        if decision.get("use_tool", False):
            tool_name = decision.get("tool_name")
            tool_input = decision.get("tool_input", {})
            
            # Get and execute the appropriate tool
            tool = get_tool(tool_name)
            if tool:
                tool_output = await tool.execute(**tool_input)
                
                # Generate a response that incorporates the tool output
                context_prompt = f"""
                The user asked: "{query}"
                
                I used the {tool_name} tool with these parameters: {tool_input}
                The tool returned this information: {tool_output}
                
                Please provide a helpful, natural-sounding response that answers the user's question
                using this information.
                """
                
                response = await get_llm_response(context_prompt)
                
                return {
                    "response": response,
                    "tool_used": tool_name,
                    "tool_input": tool_input,
                    "tool_output": tool_output
                }
            else:
                # Fallback to LLM if tool not found
                return {
                    "response": f"I wanted to use the {tool_name} tool, but it's not available. Let me answer based on my knowledge instead: " + 
                               await get_llm_response(query)
                }
        else:
            # Use LLM for general knowledge
            return {
                "response": await get_llm_response(query)
            }
    except Exception as e:
        # Fallback to LLM on parsing error
        return {
            "response": await get_llm_response(query),
            "error": str(e)
        } 