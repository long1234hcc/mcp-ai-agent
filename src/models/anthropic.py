import anthropic
from anthropic import AsyncAnthropic
from typing import List, Dict, Any, Optional
from config.settings import settings

class ClaudeModel:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.AGENT_MODEL_ID

    async def generate_response(
        self, 
        messages: List[Dict], 
        system_prompt: str,
        tools: List[Dict] = None
    ) -> Any:
        """
        Gửi request tới Claude API với System Prompt và Tools.
        """
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": messages,
                "system": system_prompt,
                "temperature": 0.0
            }

            # Chỉ thêm tools nếu có
            if tools:
                kwargs["tools"] = tools

            # Gọi API
            response = await self.client.messages.create(**kwargs)
            return response
            
        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            raise e