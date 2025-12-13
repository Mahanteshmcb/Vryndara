import sys
import os
import requests
from duckduckgo_search import DDGS # Using the web browser

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sdk.python.vryndara.client import AgentClient

AGENT_ID = "researcher-1"
GATEWAY_URL = "http://localhost:8081/api/v1/progress"

def search_web(topic):
    # CLEAN THE QUERY: Remove "Find facts about" to get better results
    clean_query = topic.replace("Find interesting facts about", "") \
                       .replace("Find facts about", "") \
                       .replace("Research", "") \
                       .strip()
    
    print(f"    [Search] Browsing web for keywords: '{clean_query}'...")
    
    results = []
    try:
        with DDGS() as ddgs:
            # Get 3 results
            for r in ddgs.text(clean_query, max_results=3):
                # Filter out junk "Google Help" results
                if "Google Help" not in r['title'] and "Android" not in r['title']:
                    results.append(f"- {r['title']}: {r['body']}")
        
        if not results:
            return "No relevant data found (filtered out junk results)."
            
        summary = "\n".join(results)
        print(f"    [Search] Found {len(results)} relevant pages.")
        return summary
    except Exception as e:
        print(f"    [Search] Error: {e}")
        return f"Search failed for {topic}"

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        topic = signal.payload
        
        # 1. Do the work
        research_data = search_web(topic)
        
        # 2. Format for the next agent
        final_output = f"RESEARCH DATA FOR: {topic}\n\n{research_data}"

        # 3. Send result
        client.send(signal.source_agent_id, "TASK_RESULT", final_output)

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
    print("🕵️ Researcher Agent (Web) Online.")
    client.listen(on_message)