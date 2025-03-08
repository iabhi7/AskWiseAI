from typing import Dict, Any, Optional
import re
from app.llm_service import get_llm_response
from app.tools import get_tool, list_tools

# Enhanced routing prompt with better tool descriptions and examples
ROUTING_PROMPT = """
You are an AI assistant that can answer questions directly or use specialized tools when necessary.
Your goal is to provide the most accurate and helpful response to the user.

WHEN TO USE TOOLS:
- Use tools ONLY for real-time or specialized information that you cannot know with certainty
- For general knowledge, opinions, or explanations, answer directly without using tools
- Never make up or guess information that should come from a tool

AVAILABLE TOOLS:
{tool_descriptions}

INSTRUCTIONS:
1. Carefully analyze the user query
2. Determine if you need real-time or specialized information to answer accurately
3. If yes, select the most appropriate tool and specify the exact parameters needed
4. If no, indicate you'll answer directly

Respond with JSON in this format:
{{
  "use_tool": true/false,
  "reasoning": "Brief explanation of your decision",
  "tool_name": "tool_name" (if use_tool is true),
  "tool_input": {{key-value parameters for the tool}} (if use_tool is true)
}}

USER QUERY: {query}
"""

async def route_query(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Route the query to either the LLM or an appropriate tool
    
    Args:
        query: The user's query
        context: Optional conversation context
    
    Returns:
        Response data including the answer and any tool usage
    """
    # Get all available tools with descriptions
    tools = list_tools()
    
    # Format tool descriptions for the prompt
    tool_descriptions = ""
    for name, info in tools.items():
        tool_descriptions += f"- {name}: {info['description']}\n"
        tool_descriptions += "  Parameters:\n"
        for param_name, param_info in info['parameters'].items():
            tool_descriptions += f"    - {param_name}: {param_info['description']}\n"
    
    # Include conversation context if provided
    context_section = ""
    if context:
        context_section = f"""
        CONVERSATION CONTEXT:
        {context}
        
        Consider the conversation context above when deciding how to respond.
        If the user refers to something mentioned earlier, use the context to understand what they mean.
        """
    
    # Ask LLM to decide whether to use a tool
    routing_prompt = f"""
    You are an AI assistant that can answer questions directly or use specialized tools when necessary.
    Your goal is to provide the most accurate and helpful response to the user.
    
    {context_section}
    
    WHEN TO USE TOOLS:
    - Use tools ONLY for real-time or specialized information that you cannot know with certainty
    - For general knowledge, opinions, or explanations, answer directly without using tools
    - Never make up or guess information that should come from a tool
    
    AVAILABLE TOOLS:
    {tool_descriptions}
    
    INSTRUCTIONS:
    1. Carefully analyze the user query
    2. Determine if you need real-time or specialized information to answer accurately
    3. If yes, select the most appropriate tool and specify the exact parameters needed
    4. If no, indicate you'll answer directly
    
    Respond with JSON in this format:
    {{
      "use_tool": true/false,
      "reasoning": "Brief explanation of your decision",
      "tool_name": "tool_name" (if use_tool is true),
      "tool_input": {{key-value parameters for the tool}} (if use_tool is true)
    }}
    
    USER QUERY: {query}
    """
    
    # Ask LLM to decide whether to use a tool
    routing_decision = await get_llm_response(
        routing_prompt,
        response_format={"type": "json_object"},
        temperature=0.1  # Lower temperature for more consistent tool selection
    )
    
    # Log the routing decision for debugging
    print(f"Routing decision: {routing_decision}")
    
    # Parse the routing decision
    try:
        decision = routing_decision
        
        if decision.get("use_tool", False):
            tool_name = decision.get("tool_name")
            tool_input = decision.get("tool_input", {})
            reasoning = decision.get("reasoning", "")
            
            # Get and execute the appropriate tool
            tool = get_tool(tool_name)
            if tool:
                # Log tool usage
                print(f"Using tool: {tool_name} with parameters: {tool_input}")
                
                try:
                    tool_output = await tool.execute(**tool_input)
                    
                    # Generate a response that incorporates the tool output
                    context_prompt = f"""
                    The user asked: "{query}"
                    
                    I used the {tool_name} tool with these parameters: {tool_input}
                    The tool returned this information: {tool_output}
                    
                    Please provide a helpful, natural-sounding response that answers the user's question
                    using this information. If the tool returned an error, explain the issue to the user.
                    """
                    
                    response = await get_llm_response(context_prompt)
                    
                    return {
                        "response": response,
                        "tool_used": tool_name,
                        "tool_input": tool_input,
                        "tool_output": tool_output,
                        "reasoning": reasoning
                    }
                except Exception as e:
                    # Handle tool execution errors
                    error_message = f"Error executing {tool_name} tool: {str(e)}"
                    print(error_message)
                    
                    # Fallback to LLM with error context
                    fallback_prompt = f"""
                    The user asked: "{query}"
                    
                    I tried to use the {tool_name} tool, but encountered an error: {str(e)}
                    
                    Please provide a helpful response that explains the issue and offers an alternative
                    answer based on your knowledge, clearly indicating the limitations.
                    """
                    
                    response = await get_llm_response(fallback_prompt)
                    
                    return {
                        "response": response,
                        "error": error_message
                    }
            else:
                # Fallback to LLM if tool not found
                return {
                    "response": f"I wanted to use the {tool_name} tool, but it's not available. Let me answer based on my knowledge instead: " + 
                               await get_llm_response(query)
                }
        else:
            # Use LLM for general knowledge
            reasoning = decision.get("reasoning", "")
            print(f"Using LLM directly. Reasoning: {reasoning}")
            
            return {
                "response": await get_llm_response(query),
                "reasoning": reasoning
            }
    except Exception as e:
        # Fallback to LLM on parsing error
        error_message = f"Error in routing decision: {str(e)}"
        print(error_message)
        
        return {
            "response": await get_llm_response(query),
            "error": error_message
        } 