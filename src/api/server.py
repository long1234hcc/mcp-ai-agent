import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.settings import settings
from src.api import routes
from src.api import dependencies
from src.core.agent import MCPAgent

# --- LIFESPAN MANAGER ---
# Logic chạy khi Server Bật/Tắt
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 [STARTUP] Initializing MCP Agent...")
    
    # 1. Khởi tạo Agent (Kết nối LLM, Load Tools)
    dependencies.global_agent = MCPAgent()
    
    print("✅ [STARTUP] Agent is ready to serve!")
    
    yield # Server chạy tại đây
    
    # 2. Cleanup (khi tắt server)
    print("\n🛑 [SHUTDOWN] Cleaning up resources...")
    dependencies.global_agent = None

# --- APP SETUP ---
app = FastAPI(
    title=settings.APP_NAME,
    description="Industrial AI Agent with MCP Architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Đăng ký Router
app.include_router(routes.router, prefix="/api/v1")

# --- RUN CONFIG ---
if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True # Tự restart khi sửa code
    )