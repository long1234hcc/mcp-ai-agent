import json
import asyncio
from typing import List, Dict, Any

# Import modules
from config.settings import settings
from src.mcp.registry import registry
from src.models.gemini_native import GeminiNativeModel
from src.core.session import SessionManager
from src.prompts.builder import prompt_builder

# Import Planner (MỚI)
from src.core.planner import AIPlanner
from src.core.planning import ExecutionPlan, PlanStep

class MCPAgent:
    def __init__(self):
        # 1. Khởi tạo Brain
        self.llm = GeminiNativeModel()
        # 2. Khởi tạo Planner (MỚI)
        self.planner = AIPlanner(self.llm)
        # 3. Lấy danh sách Tools
        self.tools_def = registry.get_definitions()
        
    async def run(self, user_query: str, session_id: str = "default", planning_mode: bool = False) -> Dict:
        """
        Main entry point. Hỗ trợ 2 modes: Reactive & Planning.
        """
        session = SessionManager(session_id)
        
        # 🌟 LOGIC MỚI: Tự động detect mode hoặc user force mode
        # Ở đây ta check keyword đơn giản để demo, thực tế có thể dùng LLM để classify
        if planning_mode or any(kw in user_query.lower() for kw in ["plan", "step", "analyze", "report", "complex"]):
            print(f"🧠 [MODE] Switching to PLANNING MODE for query: {user_query}")
            return await self._execute_with_plan(user_query, session)
        else:
            print(f"⚡ [MODE] Running in REACTIVE MODE")
            return await self._execute_reactive(user_query, session)

    async def _execute_with_plan(self, user_query: str, session: SessionManager) -> Dict:
        """
        Thực thi theo kế hoạch từng bước
        """
        # 1. Lập kế hoạch
        plan = await self.planner.create_plan(user_query)
        session.add_message("system", f"Start executing plan: {len(plan.steps)} steps.")
        
        final_results = []
        
        # 2. Thực thi từng bước
        for step in plan.steps:
            print(f"\n👉 [STEP {step.id}] Executing: {step.description}")
            
            # Tạo context từ các bước trước (quan trọng!)
            context_prefix = ""
            if final_results:
                context_prefix = "Previous steps results:\n" + "\n".join(final_results) + "\n\n"
            
            # Gọi đệ quy hàm reactive cho từng step nhỏ
            # Query thực thi = Kết quả cũ + Mô tả bước hiện tại
            step_query = f"{context_prefix}Current Task: {step.description}"
            
            # Chạy reactive mode cho step này
            step_response = await self._execute_reactive(step_query, session, is_subtask=True)
            
            # Lưu kết quả
            result_text = step_response.get("answer", "No answer")
            step.result = result_text
            step.status = "completed"
            
            final_results.append(f"Step {step.id}: {result_text}")
            session.add_message("system", f"Completed Step {step.id}: {result_text}")

        # 3. Tổng hợp kết quả cuối cùng
        summary_query = "Based on the following execution results, provide a final comprehensive answer to the user request:\n" + "\n".join(final_results)
        
        final_response = await self._execute_reactive(summary_query, session, is_subtask=False)
        
        return {
            "status": "success",
            "answer": final_response.get("answer"),
            "plan": [s.dict() for s in plan.steps], # Trả về plan để UI hiển thị
            "session_id": session.session_id
        }

    async def _execute_reactive(self, user_query: str, session: SessionManager, is_subtask: bool = False) -> Dict:
            """
            Logic ReAct cũ (đã tách ra hàm riêng)
            """
            if not is_subtask:
                session.add_message("user", user_query)
                history = session.get_messages_for_llm()
            else:
                history = session.get_messages_for_llm()
                history.append({"role": "user", "content": user_query}) 
            # -----------------------------------
            
            system_prompt = prompt_builder.build_system_prompt(self.tools_def)
            
            max_iterations = 5 
            loop_count = 0
            tool_steps = []

            while loop_count < max_iterations:
                loop_count += 1
                
                response = await self.llm.generate_response(
                    messages=history,
                    system_prompt=system_prompt,
                    tools=self.tools_def
                )
                
                ai_msg = response.choices[0].message
                content = ai_msg.content or ""
                tool_calls = ai_msg.tool_calls
                
                # CASE 1: Tool Use
                if tool_calls:
                    print(f"  🛠️  [Subtask] Using {len(tool_calls)} tools...")
                    
                    msg_assistant = {"role": "assistant", "content": content}
                    if tool_calls:
                        tool_calls_data = [{
                            "id": tc.id, "type": tc.type,
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        } for tc in tool_calls]
                        msg_assistant["tool_calls"] = tool_calls_data
                    
                    history.append(msg_assistant)
                    
                    if not is_subtask:
                        session.add_message("assistant", content, tool_calls=tool_calls_data)
                    
                    for tc in tool_calls:
                        func_name = tc.function.name
                        args_str = tc.function.arguments
                        tool_call_id = tc.id
                        
                        try:
                            args = json.loads(args_str)
                            result = await registry.execute_tool(func_name, args)
                            
                            history.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": str(result)
                            })
                            
                            if not is_subtask:
                                session.add_message("tool", str(result), tool_call_id=tool_call_id)
                                
                            tool_steps.append({"tool": func_name, "result": str(result)[:50]})
                            
                        except Exception as e:
                            print(f"   ❌ Tool Error: {e}")
                            history.append({"role": "tool", "tool_call_id": tool_call_id, "content": f"Error: {e}"})

                    continue
                
                # CASE 2: Final Answer
                else:
                    final_answer = content or ""
                    if not is_subtask:
                        session.add_message("assistant", final_answer)
                    
                    return {
                        "status": "success",
                        "answer": final_answer,
                        "steps": tool_steps
                    }
                    
            return {"status": "error", "answer": "Max iterations reached"}