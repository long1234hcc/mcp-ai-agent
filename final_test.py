# final_test.py
import requests
import json

URL = "http://localhost:8000/api/v1/chat"

# final_test.py (Sửa lại đoạn này)
def send_query(text):
    print(f"\nUser: {text}")
    try:
        resp = requests.post(URL, json={"query": text, "session_id": "test-user-1"})
        
        # In ra status code để biết lỗi gì (200 là OK, 500 là Server Lỗi)
        print(f"Server Status: {resp.status_code}")
        
        data = resp.json()
        
        # Nếu server trả về lỗi, in ra lỗi chi tiết
        if resp.status_code != 200:
            print(f"❌ SERVER ERROR DETAILS: {data}")
            return

        print(f"Agent: {data['answer']}")
        if data.get('steps'):
            print("Tools used:")
            for step in data['steps']:
                print(f"  - {step['tool']}: {step['result']}")
                
    except Exception as e:
        print(f"Client Exception: {e}")

# Case 1: Hỏi xã giao (Không dùng tool)
send_query("Hello, who are you?")

# Case 2: Hỏi System Health (Dùng Perception Tool)
send_query("Check system health for me.")

# Case 3: Hỏi khó (Chain Tools: Check CPU -> Search Fix)
send_query("If the CPU is high, find a solution to fix it.")