import json
import os
import time
from typing import List, Dict

SESSION_DIR = "workspace/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

class SessionManager:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.file_path = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
        self.messages: List[Dict] = []
        self._load_history()

    def _load_history(self):
        """Đọc file JSONL để lấy lại lịch sử chat cũ"""
        if not os.path.exists(self.file_path):
            return
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.messages.append(json.loads(line))
        except Exception as e:
            print(f"⚠️ Error loading session {self.session_id}: {e}")

    def add_message(self, role: str, content: str, tool_calls=None, tool_call_id=None):
        """Thêm message vào RAM và lưu xuống file"""
        msg = {"role": role, "content": content, "timestamp": time.time()}
        
        # Nếu là tool output, cần ID để khớp với request
        if role == "tool":
            msg["tool_call_id"] = tool_call_id
            
        # Nếu assistant gọi tool, lưu structure tool_calls
        if tool_calls:
            msg["tool_calls"] = tool_calls

        self.messages.append(msg)
        self._append_to_file(msg)

    def _append_to_file(self, msg: Dict):
        """Ghi 1 dòng vào cuối file"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg) + "\n")

    def get_messages_for_llm(self) -> List[Dict]:
        """Convert format nội bộ sang format OpenAI cần"""
        # OpenAI chỉ cần role, content, tool_calls, tool_call_id
        clean_msgs = []
        for m in self.messages:
            clean_msg = {
                "role": m["role"],
                "content": m["content"]
            }
            if "tool_calls" in m:
                clean_msg["tool_calls"] = m["tool_calls"]
            if "tool_call_id" in m:
                clean_msg["tool_call_id"] = m["tool_call_id"]
                
            clean_msgs.append(clean_msg)
        return clean_msgs

    def clear(self):
        """Xóa lịch sử"""
        self.messages = []
        if os.path.exists(self.file_path):
            os.remove(self.file_path)