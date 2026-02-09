import google.generativeai as genai
from config.settings import settings
import json
import traceback

# --- 1. HELPER: LÀM SẠCH SCHEMA (CRITICAL FIX) ---
def _sanitize_schema(schema):
    """
    Google Gemini API rất khắt khe, không chấp nhận trường 'default' 
    hoặc 'additionalProperties' trong Schema. Hàm này sẽ đệ quy để xóa chúng.
    """
    if not isinstance(schema, dict):
        return schema
    
    clean = {}
    for k, v in schema.items():
        # Xóa các key mà Google không hỗ trợ
        if k in ["default", "additionalProperties", "anyOf"]:
            continue
            
        # Đệ quy xử lý nested properties
        if k == "properties" and isinstance(v, dict):
            clean[k] = {pk: _sanitize_schema(pv) for pk, pv in v.items()}
        elif k == "items" and isinstance(v, dict):
            clean[k] = _sanitize_schema(v)
        else:
            clean[k] = v
            
    return clean

# --- 2. MOCK CLASSES (Để Agent không bị lỗi) ---
class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.type = "function"
        self.function = MockFunction(name, arguments)

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, content, tool_calls=None):
        self.choices = [MockChoice(MockMessage(content, tool_calls))]

# --- 3. CLASS CHÍNH ---
class GeminiNativeModel:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model_name = settings.AGENT_MODEL_ID

    async def generate_response(self, messages, system_prompt, tools=None):
        try:
            # A. PREPARE TOOLS
            google_tools_config = None
            if tools:
                funcs = []
                for t in tools:
                    # FIX: Làm sạch schema trước khi gửi
                    clean_parameters = _sanitize_schema(t["input_schema"])
                    
                    funcs.append({
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": clean_parameters
                    })
                
                # Google format
                google_tools_config = [{"function_declarations": funcs}]

            # B. INIT MODEL
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                tools=google_tools_config
            )

            # C. PREPARE HISTORY
            gemini_contents = []
            
            for msg in messages:
                role = msg["role"]
                content = msg.get("content", "")
                
                if role == "system": continue
                
                parts = []
                # Xử lý nội dung text/list
                text_content = ""
                if isinstance(content, str):
                    text_content = content
                elif isinstance(content, list): 
                    text_content = json.dumps(content)
                
                # Mapping Role
                if role == "tool":
                    # Tool Result -> User Text (Hack an toàn cho MVP)
                    role = "user" 
                    text_content = f"Tool Output [{msg.get('tool_call_id', 'unknown')}]: {text_content}"
                elif role == "assistant":
                    role = "model"
                
                if text_content:
                    parts.append({"text": text_content})
                
                if parts:
                    gemini_contents.append({"role": role, "parts": parts})

            # Fallback history rỗng
            if not gemini_contents:
                gemini_contents.append({"role": "user", "parts": [{"text": "Hello"}]})

            # D. EXECUTE (Stateless)
            response = await model.generate_content_async(
                contents=gemini_contents,
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            # E. PARSE RESPONSE
            final_text = ""
            tool_calls = []
            
            if response.candidates:
                # Kiểm tra safety
                if not response.candidates[0].content.parts:
                     return MockResponse(content="[Safety Filter Blocked Response]")

                for part in response.candidates[0].content.parts:
                    if part.text:
                        final_text += part.text
                    
                    if part.function_call:
                        fc = part.function_call
                        # Convert args
                        args = {}
                        if hasattr(fc, 'args'):
                            for key, value in fc.args.items():
                                args[key] = value
                            
                        tool_calls.append(MockToolCall(
                            id="call_" + fc.name,
                            name=fc.name,
                            arguments=json.dumps(args)
                        ))

            return MockResponse(
                content=final_text if final_text else None, 
                tool_calls=tool_calls if tool_calls else None
            )

        except Exception as e:
            traceback.print_exc()
            return MockResponse(content=f"Error connecting to Gemini: {str(e)}")