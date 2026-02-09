import os
from jinja2 import Environment, FileSystemLoader

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(CURRENT_DIR, "templates")

class PromptBuilder:
    def __init__(self):
        # Khởi tạo Jinja2 Environment
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def build_system_prompt(self, tools: list) -> str:
        """Render Orchestrator Prompt với danh sách tools"""
        template = self.env.get_template("orchestrator.jinja2")
        
        # Format tool descriptions cho đẹp
        tool_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
        
        return template.render(tool_descriptions=tool_desc)

    def build_evaluation_prompt(self, query: str, answer: str, history: list) -> str:
        """Render Self-Evaluation Prompt"""
        template = self.env.get_template("self_evaluation.jinja2")
        
        # Lọc lịch sử dùng tool để LLM đánh giá
        tool_usage = [msg for msg in history if msg.get("role") == "user" and "tool_result" in str(msg)]
        
        return template.render(
            user_query=query,
            assistant_answer=answer,
            tool_history=str(tool_usage)
        )
    
    def build_planner_prompt(self, query: str, tools: list) -> str:
            """Render Planner Prompt"""
            template = self.env.get_template("planner.jinja2")
            
            tool_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
            
            return template.render(
                user_query=query,
                tool_descriptions=tool_desc
            )

# Singleton
prompt_builder = PromptBuilder()