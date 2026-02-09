# src/models/gemini.py
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
from config.settings import settings

class GeminiModel:
    def __init__(self):
        # Configure Key
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # System instruction (System Prompt)
        self.model_id = settings.AGENT_MODEL_ID

    async def generate_response(self, messages: list, system_prompt: str, tools: list = None):
        """
        Adapter chuyển đổi format từ MCP Agent sang Gemini format
        """
        try:
            # 1. Setup Model với System Prompt và Tools
            # Convert tools từ JSON Schema sang Format của Gemini (FunctionDeclaration)
            # Mẹo: Gemini Python SDK mới hỗ trợ tự convert từ dict tools của OpenAI/Anthropic khá tốt
            # Nhưng để an toàn, ta khai báo tools trực tiếp khi init model
            
            converted_tools = self._convert_tools(tools) if tools else None

            model = genai.GenerativeModel(
                model_name=self.model_id,
                system_instruction=system_prompt,
                tools=converted_tools
            )

            # 2. Convert History (Messages)
            # Gemini quản lý history khác Anthropic, ta cần convert
            chat_history = self._convert_messages(messages)

            # 3. Start Chat & Send Message
            # Lấy message cuối cùng của user để gửi
            last_msg = messages[-1]['content']
            
            # Nếu history rỗng, chỉ gửi message cuối
            if not chat_history:
                chat = model.start_chat(history=[])
            else:
                # Loại bỏ message cuối cùng khỏi history vì nó là input của hàm send_message
                chat = model.start_chat(history=chat_history[:-1])

            response = await chat.send_message_async(last_msg)
            
            return response

        except Exception as e:
            print(f"❌ Gemini Error: {str(e)}")
            raise e

    def _convert_tools(self, tools):
        """
        Gemini SDK chấp nhận list of functions hoặc function declarations.
        Ở mức MVP này, để đơn giản, ta sẽ trả về list dicts raw, 
        SDK của Google hiện tại đã thông minh để tự map.
        """
        # Google SDK yêu cầu 'function_declarations' bọc ngoài
        return tools

    def _convert_messages(self, messages):
        """Convert list dict [{'role': 'user', 'content': '...'}] -> Gemini Format"""
        gemini_history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            
            # Gemini không chấp nhận System role trong history (đã để ở init)
            if msg["role"] == "system":
                continue
                
            parts = [msg["content"]]
            gemini_history.append({"role": role, "parts": parts})
        return gemini_history