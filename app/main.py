from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from app.router import route_query
from app.llm_service import get_llm_response

app = FastAPI(title="AI Q&A System")

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Route the query to either LLM or a tool
        result = await route_query(request.query)
        
        return QueryResponse(
            response=result["response"],
            tool_used=result.get("tool_used"),
            tool_input=result.get("tool_input"),
            tool_output=result.get("tool_output")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 