from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AgentResponse(BaseModel):
    """Cấu trúc trả về cuối cùng cho API"""
    answer: str
    tool_steps: List[Dict] = Field(default_factory=list) # Lưu lại các bước đã dùng tool
    confidence: float = 0.0
    is_refed: bool = False # Đã qua bước tự sửa chưa