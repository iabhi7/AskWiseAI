from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import time

from app.router import route_query
from app.llm_service import get_llm_response
from app.memory import conversation_memory
from app.cache import llm_cache, tool_cache
from app.utils.logging import logger

app = FastAPI(title="AskWiseAI - AI Q&A System")

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    conversation_id: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")
        
        # Get or create conversation ID
        conversation_id = request.conversation_id
        if not conversation_id or conversation_id not in conversation_memory.conversations:
            conversation_id = conversation_memory.create_conversation()
            logger.info(f"Created new conversation: {conversation_id}")
        else:
            logger.info(f"Using existing conversation: {conversation_id}")
        
        # Add user message to conversation history
        conversation_memory.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.query
        )
        
        # Get conversation context
        context = conversation_memory.get_conversation_context(conversation_id, max_turns=3)
        
        # Route the query to either LLM or a tool, with conversation context
        logger.info(f"Routing query with context length: {len(context) if context else 0}")
        result = await route_query(request.query, context=context if context else None)
        
        # Log tool usage if applicable
        if "tool_used" in result:
            logger.info(f"Used tool: {result['tool_used']}")
        
        # Add assistant response to conversation history
        conversation_memory.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"],
            metadata={
                "tool_used": result.get("tool_used"),
                "tool_input": result.get("tool_input"),
                "tool_output": result.get("tool_output")
            }
        )
        
        logger.info(f"Returning response for query: {request.query[:30]}...")
        
        return QueryResponse(
            response=result["response"],
            conversation_id=conversation_id,
            tool_used=result.get("tool_used"),
            tool_input=result.get("tool_input"),
            tool_output=result.get("tool_output")
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    # Clean expired conversations and cache entries
    expired_convs = conversation_memory.clean_expired_conversations()
    expired_cache = tool_cache.remove_expired() + llm_cache.remove_expired()
    
    logger.info(f"Health check: {len(conversation_memory.conversations)} active conversations, "
                f"{expired_convs} expired conversations removed, "
                f"{expired_cache} expired cache entries removed")
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "stats": {
            "active_conversations": len(conversation_memory.conversations),
            "expired_conversations_removed": expired_convs,
            "expired_cache_entries_removed": expired_cache
        }
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id in conversation_memory.conversations:
        del conversation_memory.conversations[conversation_id]
        logger.info(f"Deleted conversation: {conversation_id}")
        return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
    else:
        logger.warning(f"Attempted to delete non-existent conversation: {conversation_id}")
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

if __name__ == "__main__":
    logger.info("Starting AskWiseAI server")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 