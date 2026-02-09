from pydantic import BaseModel, Field
from typing import List, Optional

class PlanStep(BaseModel):
    id: int
    description: str = Field(..., description="Mô tả nhiệm vụ cần làm bằng ngôn ngữ tự nhiên")
    tool_hint: Optional[str] = Field(None, description="Gợi ý tool nên dùng (nếu biết)")
    status: str = "pending" # pending, running, completed, failed
    result: Optional[str] = None

class ExecutionPlan(BaseModel):
    original_query: str
    steps: List[PlanStep]
    current_step_index: int = 0