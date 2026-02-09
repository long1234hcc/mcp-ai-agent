# MCP AI Agent Orchestrator (MVP)

Hệ thống AI Agent thông minh sử dụng kiến trúc Model Context Protocol (MCP) để điều phối các công cụ giám sát công nghiệp, với khả năng tự đánh giá và sửa lỗi (Self-Correction).

## 🏗️ Kiến trúc Hệ thống

1.  **API Layer (`src/api`):** Cổng giao tiếp RESTful (FastAPI).
2.  **Core Layer (`src/core`):** Bộ não điều phối (Agent Logic & Session).
3.  **MCP Layer (`src/mcp`):** Tầng giao thức kết nối Tools.
4.  **Tools Layer (`tools/`):** Các module chức năng (Mock Implementation).

## 🛠️ Setup & Run

1.  **Cài đặt:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Cấu hình:**
    - Copy `.env.example` thành `.env`
    - Điền API Key của bạn.
3.  **Chạy Server:**
    ```bash
    python -m src.api.server
    ```