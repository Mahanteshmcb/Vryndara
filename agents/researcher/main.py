import sys
import os
import time
import json
import requests

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from duckduckgo_search import DDGS
from sdk.python.vryndara.client import AgentClient

AGENT_ID = "researcher-1"
GATEWAY_URL = "http://localhost:8081/api/v1/progress"

def search_web(query):
    print(f"    [Search] Googling: '{query}'...")
    results = []
    try:
        # Use DuckDuckGo to get real results
        with DDGS() as ddgs:
            # Get top 3 results
            for r in ddgs.text(query, max_results=3):
                results.append(f"- {r['title']}: {r['body']}")
        
        # Combine into a summary
        summary = "\n".join(results)
        print(f"    [Search] Found {len(results)} facts.")
        return summary
    except Exception as e:
        print(f"    [Search] Error: {e}")
        return "Could not fetch web data. Using internal knowledge."

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        topic = signal.payload
        
        # 1. Do the work (Real Search)
        print(f"    [Work] Researching: {topic}")
        research_data = search_web(topic)
        
        # 2. Add a formatted header for the next agent
        final_output = f"RESEARCH REPORT ON: {topic}\n\n{research_data}"

        # 3. Send result back to Kernel
        client.send(
            target_id=signal.source_agent_id,
            msg_type="TASK_RESULT",
            payload=final_output
        )

        # 4. Update UI
        try:
            requests.post(GATEWAY_URL, json={
                "workflow_id": "demo-flow",
                "agent_id": AGENT_ID,
                "status": "COMPLETED",
                "result_url": "view-in-logs"
            })
            print("    [UI] ✅ Status pushed.")
        except:
            pass

if __name__ == "__main__":
    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["research.web", "knowledge.retrieval"])
    print("🕵️ Researcher Agent Online. Ready to browse.")
    client.listen(on_message)