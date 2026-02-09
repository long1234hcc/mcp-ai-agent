import requests
import json
import time # <--- Import time

URL = "http://localhost:8000/api/v1/chat"

def send_query(text):
    print(f"\nUser: {text}")
    try:
        resp = requests.post(URL, json={"query": text, "session_id": "test-user-1"})
        
        if resp.status_code != 200:
            print(f"❌ Error: {resp.text}")
            return

        data = resp.json()
        print(f"Agent: {data['answer']}")
        if data.get('steps'):
            print("Tools used:")
            for step in data['steps']:
                print(f"  - {step['tool']}: {step['result'][:50]}...") # Cắt ngắn cho gọn
    except Exception as e:
        print(f"Error: {e}")

# Case 1
send_query("Hello, who are you?")
print("\n⏳ Waiting 20s for Rate Limit...")
time.sleep(20) # Chờ 20 giây

# Case 2
send_query("Check system health for me.")
print("\n⏳ Waiting 20s for Rate Limit...")
time.sleep(20) # Chờ 20 giây

# Case 3
send_query("If the CPU is high, find a solution to fix it.")