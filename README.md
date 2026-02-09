# 🤖 Industrial AI Agent Orchestrator  
**Deep Dive Architecture Documentation**

- **Version:** 2.0 (Technical Deep Dive)  
- **Author:** [Tên của bạn]  
- **Tech Stack:** Python, FastAPI, Google Gemini 1.5, Jinja2, Pydantic  

---

## 📌 Tổng Quan Dự Án

Dự án này là một **Autonomous AI Agent** được thiết kế theo kiến trúc **Modular Monolith**.

Khác với các chatbot thông thường, Agent có khả năng:

- 🧠 **Reasoning** – Suy luận
- 🗂️ **Planning** – Lập kế hoạch
- 🛠️ **Tool Use** – Sử dụng công cụ

Agent có thể tương tác với **hệ thống công nghiệp giả lập** thông qua các tool động.

---

## 🗺️ 1. Luồng Hoạt Động (Request Lifecycle)

Dưới đây là hành trình của một request từ lúc user gửi tin nhắn đến khi nhận phản hồi:

### 🔹 Bước 1: Input
User gửi request qua API, ví dụ:


---

### 🔹 Bước 2: Session Manager
- Tải lịch sử chat cũ của user từ file **JSONL**
- Cung cấp **context** cho Agent

---

### 🔹 Bước 3: Prompt Builder
- Load template `orchestrator.jinja2`
- Tự động inject danh sách tool hiện có
- Sinh ra **System Prompt hoàn chỉnh**

---

### 🔹 Bước 4: Planner (Decision Maker)

- **Reactive Mode**
  - Gửi prompt + history + tool definitions trực tiếp sang LLM

- **Planning Mode**
  - Tách yêu cầu thành các bước nhỏ:
    ```
    Check → Search → Report
    ```

---

### 🔹 Bước 5: LLM Execution (Gemini Adapter)
- Chuyển format OpenAI → Google Gemini
- Làm sạch schema
- Gửi request lên Google Cloud

---

### 🔹 Bước 6: Tool Registry
- Nếu LLM yêu cầu dùng tool (vd: `perception_monitor`)
- Registry ánh xạ tool name → hàm Python tương ứng
- Thực thi tool

---

### 🔹 Bước 7: ReAct Loop
- Kết quả tool được gửi ngược lại LLM
- LLM suy luận tiếp
- Lặp cho đến khi có kết quả cuối cùng

---

## 🔍 2. Chi Tiết Kỹ Thuật (Deep Dive Components)

### 2.1. Dynamic Tool Registry

#### ❓ Vấn đề
Làm sao để thêm tool mới **mà không sửa code lõi (`agent.py`)**?

#### ✅ Giải pháp
**Auto-Discovery Mechanism**

#### 🔧 Cách hoạt động
- Mỗi tool nằm trong thư mục `tools/`
- Mỗi tool là một folder chứa file `tool.py`
- `tool.py` bắt buộc có:
  - `DEFINITION`: mô tả tool
  - `async def execute(...)`

- File `src/mcp/registry.py`:
  - Quét thư mục `tools/`
  - Import động (dynamic import)
  - Lưu vào Dictionary:
    ```python
    {
      "tool_name": function_pointer
    }
    ```

- Khi LLM trả về tên tool → Registry thực thi đúng hàm

---

### 2.2. Prompt Engineering & Template Injection

#### ❓ Vấn đề
Prompt dài, hardcode trong Python → khó bảo trì

#### ✅ Giải pháp
**Jinja2 Templating Engine**

#### 🔧 Cách hoạt động
- Template nằm tại:


- Có các placeholder:
```jinja2
{{ tool_descriptions }}

src/prompts/templates/orchestrator.jinja2


- Có các placeholder:
```jinja2
{{ tool_descriptions }}


PromptBuilder:

Lấy danh sách tools từ Registry

Format thành text

Inject vào template

👉 System Prompt luôn tự động cập nhật theo tool thực tế

2.3. Session Management & Persistence
❓ Vấn đề

Agent cần nhớ user là ai, đã nói gì trước đó

✅ Giải pháp

File-based Persistence (JSONL)

🔧 Cách hoạt động

Mỗi session_id → một file .jsonl

Thư mục:

workspace/sessions/


Khi có request mới:

Load session lên RAM

Append ngay lập tức mọi message:

User

Assistant

Tool Result

📌 Vì sao dùng JSONL?

Dễ debug

Không cần database

Phù hợp MVP / Prototype

2.4. LLM Adapter (Google Gemini Native)
❓ Vấn đề

Logic Agent viết theo chuẩn OpenAI

Google Gemini có format hoàn toàn khác

✅ Giải pháp

Adapter Pattern

📂 File:

src/models/gemini_native.py

🔧 Chức năng chính

Translation

OpenAI messages → Gemini contents

Schema Sanitization (Quan trọng)

Gemini không chấp nhận:

default

title

các field thừa trong schema

Hàm _sanitize_schema() lọc bỏ các field này

Stateless Execution

Dùng generate_content

Không dùng chat_session

Tránh xung đột state với SessionManager

📂 3. Cấu Trúc Thư Mục (Project Tree)

mcp-ai-agent/
├── config/
│   └── settings.py          # Load env, validate config
│
├── src/
│   ├── api/                 # Interface Layer
│   │   ├── server.py        # FastAPI entrypoint
│   │   ├── routes.py        # API endpoints (/chat)
│   │   └── dependencies.py # Dependency Injection
│   │
│   ├── core/                # Business Logic
│   │   ├── agent.py         # [BRAIN] ReAct loop
│   │   ├── planner.py       # [STRATEGIST] Planning logic
│   │   ├── planning.py      # Plan models (Pydantic)
│   │   ├── session.py       # [MEMORY] JSONL persistence
│   │   └── message.py       # Internal message schema
│   │
│   ├── mcp/
│   │   └── registry.py      # [TOOL MANAGER]
│   │
│   ├── models/
│   │   └── gemini_native.py # [ADAPTER]
│   │
│   └── prompts/
│       ├── builder.py
│       └── templates/
│
├── tools/
│   ├── perception_monitor/
│   ├── rag_search/
│   └── ...
│
├── workspace/
│   └── sessions/
│
├── .env
├── requirements.txt
└── README.md
🚀 4. Quick Start
Bước 1: Clone & Setup
git clone <repo_url>
cd mcp-ai-agent

uv venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

uv pip install -r requirements.txt
uv pip install google-generativeai

Bước 2: Cấu Hình API Key

Tạo file .env:

APP_NAME="Industrial Agent"
ENV_MODE="dev"

# Get free key at https://aistudio.google.com/
GOOGLE_API_KEY="AIzaSyD-xxxxxxxxxxxxxxxxxxxx"
AGENT_MODEL_ID="gemini-1.5-flash"

Bước 3: Chạy Server
python src/api/server.py


API: http://localhost:8000

Swagger UI: http://localhost:8000/docs

🧪 5. Testing & Demo Scenarios
✅ Scenario 1: Basic Connectivity

File: testing.py

Mục đích: kiểm tra API Key & kết nối Google

✅ Scenario 2: Reactive Mode

File: final_test.py

Flow:

User → Monitor Tool → Result → Answer

✅ Scenario 3: Planning Mode

File: test_planning.py

Flow:

Planner
 ├─ Monitor
 ├─ Search
 └─ Report

🧠 Ghi Chú Cho Team Dev

Thêm tool mới

Copy folder tools/perception_monitor

Đổi tên + sửa logic

❌ Không cần sửa agent.py

Đổi LLM (vd: GPT-4)

Viết adapter mới openai_native.py

Đổi config trong settings.py



---

Nếu bạn muốn:
- ✂️ rút gọn cho README public
- 📘 tách thành **docs/architecture.md**
- 🧠 vẽ **sơ đồ kiến trúc (Mermaid / Draw.io)**

→ nói mình, mình làm tiếp cho bạn ngay.
