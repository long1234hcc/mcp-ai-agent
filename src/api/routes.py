from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.core.agent import MCPAgent
from src.api.dependencies import get_agent

router = APIRouter()

# --- UPDATE 1: Thêm field planning_mode ---
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"
    planning_mode: bool = False # Mặc định là False (Reactive)

class ChatResponse(BaseModel):
    status: str
    answer: str
    plan: Optional[List[Dict]] = None # Trả về kế hoạch nếu có
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    agent: MCPAgent = Depends(get_agent)
):
    """
    Gửi câu hỏi cho AI Agent.
    - query: Câu hỏi
    - planning_mode: True để kích hoạt chế độ lập kế hoạch (cho task phức tạp)
    """
    try:
        # --- UPDATE 2: Truyền tham số vào agent.run ---
        response = await agent.run(
            user_query=request.query, 
            session_id=request.session_id,
            planning_mode=request.planning_mode
        )
        if "session_id" not in response:
            response["session_id"] = request.session_id
        return response
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "mcp-agent-api"}