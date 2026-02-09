from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.core.agent import MCPAgent
from src.api.dependencies import get_agent

router = APIRouter()

# Schema cho dữ liệu đầu vào
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"

# Schema cho dữ liệu đầu ra (cho đẹp document)
class ChatResponse(BaseModel):
    status: str
    answer: str
    steps: list
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    agent: MCPAgent = Depends(get_agent) # Inject Agent vào đây
):
    """
    Gửi câu hỏi cho AI Agent.
    """
    try:
        # Gọi hàm run của Agent
        response = await agent.run(
            user_query=request.query, 
            session_id=request.session_id
        )
        return response
        
    except Exception as e:
        # Log lỗi ra console server
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "mcp-agent-api"}