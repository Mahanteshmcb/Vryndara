import sys
import os
import time

# SIMULATING EXTERNAL APP CONFIGURATION
# In the real Historabook, you would pip install this package.
# Here, we point to the local folder.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'sdk/python')))

from vryndara.client import AgentClient

# 1. SETUP: Identify as an external app
APP_ID = "historabook-v1"
KERNEL_ADDRESS = "localhost:50051"

def main():
    print(f"📱 [Historabook App] Connecting to Vryndara OS at {KERNEL_ADDRESS}...")
    
    # Connect to the Kernel
    client = AgentClient(APP_ID, kernel_address=KERNEL_ADDRESS)
    client.register(["external.app"])
    
    # 2. TRIGGER: The user clicks "Generate Movie" in Historabook
    topic = "The construction of the Great Wall of China"
    print(f"🎬 [Historabook App] User requested video on: '{topic}'")
    
    # 3. ACTION: Send the request to the Workflow
    # We send it to the 'researcher-1' first, knowing the chain will handle the rest.
    target_agent = "researcher-1" 
    
    print(f"📡 [Historabook App] Sending signal to Vryndara...")
    client.send(
        target_id=target_agent, 
        msg_type="TASK_REQUEST", 
        payload=f"Find interesting facts about {topic}"
    )

    # 4. LISTEN: Wait for the result (The Video URL)
    print(f"⏳ [Historabook App] Waiting for Vryndara to finish production...")
    
    # We define a temporary listener to catch the final video
    def on_result(signal):
        if signal.type == "TASK_RESULT":
            print(f"\n🎉 [Historabook App] NOTIFICATION RECEIVED!")
            print(f"    From Agent: {signal.source_agent_id}")
            print(f"    Payload: {signal.payload[:100]}...") # Print first 100 chars
            
            if "http" in signal.payload:
                print(f"    ✅ VIDEO READY. Link captured.")
            
            # Stop the script once we have the result
            os._exit(0)

    client.listen(on_result)

if __name__ == "__main__":
    main()