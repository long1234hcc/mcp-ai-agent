import json
import asyncio
from typing import List, Dict, Any

# Import các module đã làm
from config.settings import settings
from src.mcp.registry import registry
from src.models.openai_compatible import OpenAIModel # Dùng class mới làm ở Step 4
from src.core.session import SessionManager
from src.core.message import AgentResponse
from src.prompts.builder import prompt_builder

class MCPAgent:
    def __init__(self):
        # 1. Khởi tạo Brain
        self.llm = OpenAIModel()
        # 2. Lấy danh sách Tools từ Registry
        self.tools_def = registry.get_definitions()
        
    async def run(self, user_query: str, session_id: str = "default") -> Dict:
        """
        Hàm chính thực thi logic Agent
        """
        # 1. Load Session
        session = SessionManager(session_id)
        session.add_message("user", user_query)
        
        # 2. Build System Prompt
        system_prompt = prompt_builder.build_system_prompt(self.tools_def)
        
        # 3. Reasoning Loop variables
        max_iterations = 10
        loop_count = 0
        final_answer = ""
        tool_steps = [] # Để log lại các bước đã làm
        
        print(f"\n🚀 [AGENT] Start Session: {session_id} | Query: {user_query}")

        while loop_count < max_iterations:
            loop_count += 1
            print(f"🔄 Step {loop_count}...")
            
            # A. Gọi LLM
            history = session.get_messages_for_llm()
            response = await self.llm.generate_response(
                messages=history,
                system_prompt=system_prompt,
                tools=self.tools_def # Gửi kèm định nghĩa tools
            )
            
            # Lấy message trả về từ Gemini
            ai_msg = response.choices[0].message
            content = ai_msg.content or ""
            tool_calls = ai_msg.tool_calls
            
            # B. Xử lý phản hồi
            
            # CASE 1: LLM muốn dùng Tool
            if tool_calls:
                print(f"🛠️  AI wants to use {len(tool_calls)} tools.")
                
                # Lưu message của AI vào history (để giữ context)
                # Lưu ý: Phải convert tool_calls object sang dict để serialize JSON
                tool_calls_data = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
                session.add_message("assistant", content, tool_calls=tool_calls_data)
                
                # Thực thi từng tool
                for tc in tool_calls:
                    func_name = tc.function.name
                    args_str = tc.function.arguments
                    tool_call_id = tc.id
                    
                    try:
                        args = json.loads(args_str)
                        print(f"   👉 Executing {func_name} with {args}")
                        
                        # Gọi hàm thực thi từ Registry
                        result = await registry.execute_tool(func_name, args)
                        
                        # Lưu kết quả tool vào history
                        # Quan trọng: role='tool' và tool_call_id phải khớp
                        session.add_message("tool", str(result), tool_call_id=tool_call_id)
                        
                        # Log lại step
                        tool_steps.append({"tool": func_name, "args": args, "result": str(result)[:50] + "..."})
                        
                    except Exception as e:
                        print(f"   ❌ Tool Error: {e}")
                        session.add_message("tool", f"Error: {str(e)}", tool_call_id=tool_call_id)
                
                # Sau khi chạy tool xong, loop tiếp để LLM đọc kết quả
                continue
            
            # CASE 2: LLM trả lời (Text only)
            else:
                final_answer = content
                
                # ⭐ SELF-CORRECTION CHECK ⭐
                # Logic: Nếu chưa check lần nào -> Check. Nếu check rồi thấy tệ -> Retry.
                
                # (Ở phiên bản MVP này, ta check đơn giản bằng độ dài & logic mock)
                # Để test flow, ta giả định confidence luôn cao nếu có câu trả lời dài > 20 ký tự
                confidence = 0.9 if len(final_answer) > 20 else 0.5
                
                # Lưu câu trả lời vào session
                session.add_message("assistant", final_answer)
                
                print(f"✅ Final Answer generated (Length: {len(final_answer)})")
                
                return {
                    "status": "success",
                    "answer": final_answer,
                    "steps": tool_steps,
                    "session_id": session_id
                }
                
        return {"status": "error", "answer": "Max iterations reached"}