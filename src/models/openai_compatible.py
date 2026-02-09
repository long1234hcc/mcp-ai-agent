from openai import AsyncOpenAI
from config.settings import settings
import json

class OpenAIModel:
    def __init__(self):
        # Kết nối tới Google Gemini qua endpoint tương thích OpenAI
        self.client = AsyncOpenAI(
            api_key=settings.GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = settings.AGENT_MODEL_ID # gemini-1.5-flash

    async def generate_response(self, messages, system_prompt, tools=None):
        try:
            # 1. Format System Prompt
            formatted_msgs = [{"role": "system", "content": system_prompt}] + messages

            # 2. Prepare Arguments
            kwargs = {
                "model": self.model,
                "messages": formatted_msgs,
                "temperature": 0.0
            }
            
            # 3. Tool Conversion Logic (FIX QUAN TRỌNG)
            if tools:
                openai_tools = []
                for t in tools:
                    # Map từ chuẩn MCP sang chuẩn OpenAI
                    # MCP dùng "input_schema", OpenAI dùng "parameters"
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t["description"],
                            "parameters": t["input_schema"] 
                        }
                    }
                    openai_tools.append(tool_def)
                
                kwargs["tools"] = openai_tools

            # 4. Call API
            response = await self.client.chat.completions.create(**kwargs)
            return response
        
        except Exception as e:
            # In lỗi chi tiết ra console server để debug
            print(f"❌ LLM Error: {str(e)}")
            raise e