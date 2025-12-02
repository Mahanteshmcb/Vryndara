import time
import sys
import os
import requests # <--- NEW: Needed to talk to the UI

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import ollama
from sdk.python.vryndara.client import AgentClient

AGENT_ID = "coder-alpha"
# Use the model you have installed
MODEL_NAME = "llama3.1:8b" 

# Gateway URL for reporting progress
GATEWAY_URL = "http://localhost:8081/api/v1/progress"

def generate_code(prompt):
    print(f"    [Brain] Thinking with {MODEL_NAME}...")
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': 'You are a Python coding agent. Output ONLY code.'},
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"# Error: {str(e)}"

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        user_prompt = signal.payload
        print(f"    [Task] {user_prompt}")
        
        # 1. Do the work
        start_ts = time.time()
        generated_code = generate_code(user_prompt)
        duration = round(time.time() - start_ts, 2)

        # 2. Send result to Kernel (Data)
        print(f"    [Done] Generated in {duration}s. Sending reply...")
        client.send(
            target_id=signal.source_agent_id,
            msg_type="TASK_RESULT",
            payload=generated_code
        )

        # 3. --- NEW: Send update to Gateway (UI) ---
        try:
            requests.post(GATEWAY_URL, json={
                "workflow_id": "demo-flow",
                "agent_id": AGENT_ID,
                "status": "COMPLETED",
                "result_url": "view-in-logs"
            })
            print("    [UI] ✅ Green signal sent to Dashboard.")
        except Exception as e:
            print(f"    [UI] ❌ Failed to update Dashboard: {e}")

if __name__ == "__main__":
    # Ensure requests is installed: pip install requests
    try:
        ollama.list()
        print(f"✅ Connected to Ollama. Using model: {MODEL_NAME}")
    except:
        print("❌ Error: Ollama is not running!")
        exit(1)

    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["python.generation", "ai.local"])
    client.listen(on_message)