import sys
import os
import time
import json
import requests
import ollama # <--- NEW: The Brain

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sdk.python.vryndara.client import AgentClient
from sdk.python.vryndara.storage import StorageManager

AGENT_ID = "media-director"
MODEL_NAME = "llama3.1:8b" # Using your local AI
GATEWAY_URL = "http://localhost:8081/api/v1/progress"
storage = StorageManager(bucket_name="historabook-output")

def write_screenplay(context):
    """
    Uses Llama 3 to convert raw facts into a visual screenplay.
    """
    print(f"    [Director] Thinking... turning research into a script.")
    
    prompt = f"""
    You are a Hollywood Film Director. 
    Convert the following research data into a 3-Scene Screenplay.
    
    Format:
    SCENE 1: [Visual Description]
    NARRATOR: [Dialogue]
    
    RESEARCH DATA:
    {context}
    """

    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': 'You are a creative director. Output ONLY the script.'},
            {'role': 'user', 'content': prompt},
        ])
        script = response['message']['content']
        print(f"    [Director] Script Generated ({len(script)} chars).")
        return script
    except Exception as e:
        print(f"    [Director] Error generating script: {e}")
        return "SCENE 1: Error in script generation."

def render_scene(script):
    """
    Simulates sending the screenplay to Blender/Unreal.
    In the future, this function will parse the script and command Blender.
    """
    # We save the text script as a file too, so we can see it!
    script_filename = f"script_{int(time.time())}.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script)
    
    script_url = storage.upload_file(script_filename)
    os.remove(script_filename)

    print(f"    [Video] Rendering video based on script...")
    time.sleep(3) # Simulate rendering time
    
    # Create dummy mp4
    video_filename = f"render_{int(time.time())}.mp4"
    with open(video_filename, "wb") as f:
        f.write(os.urandom(1024 * 500)) 
        
    video_url = storage.upload_file(video_filename)
    os.remove(video_filename)
    
    return script_url, video_url

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        raw_input = signal.payload
        
        # 1. INTELLIGENCE STEP: Write the Script
        # If there is context (from Researcher), Llama 3 creates the screenplay
        screenplay = write_screenplay(raw_input)
        
        # 2. ACTION STEP: Render the Video
        script_link, video_link = render_scene(screenplay)
        
        response_payload = f"SCRIPT: {script_link}\nVIDEO: {video_link}"

        # 3. Send result back
        client.send(signal.source_agent_id, "TASK_RESULT", response_payload)
        print(f"    [Done] Results uploaded.")

        # 4. Update UI
        try:
            requests.post(GATEWAY_URL, json={
                "workflow_id": "demo-flow",
                "agent_id": AGENT_ID,
                "status": "COMPLETED",
                "result_url": video_link 
            })
            print("    [UI] ✅ Status pushed.")
        except:
            pass

if __name__ == "__main__":
    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["media.video", "media.director"])
    print("🎬 Media Director Online. Waiting for scripts...")
    client.listen(on_message)