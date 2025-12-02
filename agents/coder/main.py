import time
# CLEAN IMPORT: No sys.path hacks needed!
from sdk.python.vryndara.client import AgentClient

AGENT_ID = "coder-alpha"

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    if signal.type == "TASK_REQUEST":
        time.sleep(1)
        client.send(signal.source_agent_id, "TASK_RESULT", "def clean_code(): pass")

if __name__ == "__main__":
    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["python.clean"])
    client.listen(on_message)