import requests
import json
import time

URL = "http://localhost:8000/api/v1/chat"

def test_planning_mode():
    # Một câu hỏi phức tạp yêu cầu nhiều bước
    complex_query = "Analyze the system health of 'robot_arm_01'. If there are any issues, search for solutions in the manual and generate a summary report."
    
    print(f"\n🧠 Sending Complex Query: '{complex_query}'")
    print("MODE: Planning Mode = ON")
    
    try:
        start_time = time.time()
        
        # Gửi request với planning_mode=True
        payload = {
            "query": complex_query,
            "session_id": "plan-test-01",
            "planning_mode": True
        }
        
        resp = requests.post(URL, json=payload)
        
        if resp.status_code != 200:
            print(f"❌ Error: {resp.text}")
            return

        data = resp.json()
        duration = time.time() - start_time
        
        print(f"\n✅ Request completed in {duration:.2f}s")
        
        # 1. In ra Kế hoạch (Plan)
        if data.get("plan"):
            print("\n📋 EXECUTION PLAN:")
            for step in data["plan"]:
                status_icon = "✅" if step.get('status') == 'completed' else "⏳"
                print(f"  {status_icon} [Step {step['id']}] {step['description']}")
                print(f"     -> Result: {str(step.get('result'))[:100]}...") # Cắt ngắn
        
        # 2. In ra Câu trả lời cuối cùng
        print(f"\n🤖 FINAL ANSWER:\n{data['answer']}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_planning_mode()