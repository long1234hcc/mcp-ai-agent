import importlib
import logging
from typing import List, Dict, Callable, Any

# Setup Logger
logger = logging.getLogger(__name__)

# Danh sách module cần load (đường dẫn tính từ root)
TOOL_MODULES = [
    "tools.perception_monitor.tool",
    "tools.data_system.tool",
    "tools.rag_search.tool",
    "tools.report_generator.tool",
    "tools.external_api.tool"
]

class ToolRegistry:
    def __init__(self):
        self.tools_map: Dict[str, Callable] = {}
        self.definitions: List[Dict] = []
        self._load_tools()

    def _load_tools(self):
        """Dynamic import các tool từ folder"""
        print("🛠️  Loading MCP Tools...")
        for module_path in TOOL_MODULES:
            try:
                # Import module dynamically
                mod = importlib.import_module(module_path)
                
                # Lấy biến DEFINITION và hàm execute
                definition = getattr(mod, "DEFINITION", None)
                func = getattr(mod, "execute", None)
                
                if definition and func:
                    self.definitions.append(definition)
                    self.tools_map[definition["name"]] = func
                    print(f"  ✅ Loaded: {definition['name']}")
                else:
                    print(f"  ⚠️  Skipped {module_path}: Missing DEFINITION or execute()")
            except ImportError as e:
                print(f"  ❌ Error importing {module_path}: {e}")
            except Exception as e:
                print(f"  ❌ Unexpected error in {module_path}: {e}")

    def get_definitions(self) -> List[Dict]:
        """Trả về schema cho LLM (Claude)"""
        return self.definitions

    async def execute_tool(self, name: str, arguments: dict) -> Any:
        """Thực thi tool theo tên"""
        if name not in self.tools_map:
            raise ValueError(f"Tool '{name}' not found")
        
        func = self.tools_map[name]
        try:
            # Gọi hàm async
            result = await func(**arguments)
            return result
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

# Singleton Instance
registry = ToolRegistry()