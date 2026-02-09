import json
import re
from typing import List, Dict

from src.models.gemini_native import GeminiNativeModel
from src.prompts.builder import prompt_builder
from src.core.planning import ExecutionPlan, PlanStep
from src.mcp.registry import registry

class AIPlanner:
    def __init__(self, llm: GeminiNativeModel):
        self.llm = llm

    async def create_plan(self, user_query: str) -> ExecutionPlan:
        """
        Phân tích query và tạo ra kế hoạch thực thi
        """
        # 1. Lấy danh sách tools để Planner biết mình có gì
        tools_def = registry.get_definitions()
        
        # 2. Build Prompt
        prompt = prompt_builder.build_planner_prompt(user_query, tools_def)
        
        # 3. Gọi LLM (Không dùng tools, chỉ cần trả về JSON Text)
        # Hack: Gửi prompt dưới dạng system hoặc user message đều được
        messages = [{"role": "user", "content": prompt}]
        
        print(f"📋 [PLANNER] Thinking about plan for: {user_query}")
        
        # Gọi model (lưu ý: hàm generate_response trả về MockResponse)
        response = await self.llm.generate_response(messages, system_prompt="You are a JSON generator.")
        
        content = response.choices[0].message.content
        
        # 4. Parse JSON
        try:
            # Clean JSON (đôi khi LLM trả về ```json ... ```)
            json_str = self._clean_json_text(content)
            data = json.loads(json_str)
            
            steps = []
            for item in data.get("steps", []):
                steps.append(PlanStep(
                    id=item["id"],
                    description=item["description"],
                    tool_hint=item.get("tool_hint")
                ))
            
            print(f"📋 [PLANNER] Created {len(steps)} steps.")
            return ExecutionPlan(original_query=user_query, steps=steps)
            
        except Exception as e:
            print(f"❌ Planner JSON Error: {e} \nContent: {content}")
            # Fallback: Nếu lỗi, tạo plan 1 bước duy nhất
            return ExecutionPlan(
                original_query=user_query,
                steps=[PlanStep(id=1, description=user_query, tool_hint="unknown")]
            )

    def _clean_json_text(self, text: str) -> str:
        """Xóa markdown code block nếu có"""
        text = text.strip()
        if text.startswith("```"):
            # Tìm vị trí bắt đầu và kết thúc của code block
            # Xóa dòng đầu tiên (```json) và dòng cuối (```)
            lines = text.split("\n")
            if len(lines) > 2:
                return "\n".join(lines[1:-1])
        return text