from src.core.agent import MCPAgent

# Biến toàn cục lưu instance của Agent
# Ban đầu là None, sẽ được khởi tạo khi Server start
global_agent: MCPAgent = None

def get_agent() -> MCPAgent:
    """
    Hàm Dependency để Inject Agent vào Router.
    """
    if global_agent is None:
        raise RuntimeError("Agent has not been initialized. Check server startup logic.")
    return global_agent