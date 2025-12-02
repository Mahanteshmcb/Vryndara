import sys
import os
import time
import json
import requests

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sdk.python.vryndara.client import AgentClient
from sdk.python.vryndara.storage import StorageManager

AGENT_ID = "media-director"
storage = StorageManager(bucket_name="historabook-output")

def generate_narration(text):
    """
    Simulates generating TTS audio (e.g., ElevenLabs or Coqui).
    Returns: MinIO URL to the .wav file
    """
    print(f"    [Audio] Generating narration for: '{text[:20]}...'")
    time.sleep(2) # Simulate processing time
    
    # Create a dummy .wav file
    filename = f"narration_{int(time.time())}.wav"
    with open(filename, "wb") as f:
        f.write(os.urandom(1024 * 50)) # 50KB dummy audio
    
    # Upload to "Shared Drive"
    url = storage.upload_file(filename)
    
    # Clean up local disk (agent is stateless)
    os.remove(filename)
    return url

def render_scene(scene_description):
    """
    Simulates sending a job to Blender/Unreal.
    Returns: MinIO URL to the .mp4 file
    """
    print(f"    [Video] Rendering scene: '{scene_description}'")
    time.sleep(3) # Simulate rendering time
    
    # Create a dummy .mp4 file
    filename = f"render_{int(time.time())}.mp4"
    with open(filename, "wb") as f:
        f.write(os.urandom(1024 * 500)) # 500KB dummy video
        
    url = storage.upload_file(filename)
    os.remove(filename)
    return url

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        instruction = signal.payload.lower()
        response_payload = ""

        # --- ROUTING LOGIC ---
        if "narrate" in instruction or "audio" in instruction:
            url = generate_narration(signal.payload)
            response_payload = f"AUDIO_READY: {url}"
            
        elif "render" in instruction or "video" in instruction:
            url = render_scene(signal.payload)
            response_payload = f"VIDEO_READY: {url}"
            
        else:
            response_payload = "Error: I only handle Audio or Video tasks."

        # Send result back
        client.send(signal.source_agent_id, "TASK_RESULT", response_payload)
        print(f"    [Done] Sent URL: {response_payload}")

        # --- NEW: Report to Gateway for UI Update ---
    try:
        # We assume a fake workflow ID for this demo
        requests.post("http://localhost:8081/api/v1/progress", json={
            "workflow_id": "demo-flow",
            "agent_id": AGENT_ID,
            "status": "COMPLETED",
            "result_url": url
        })
        print("    [UI] Status pushed to Gateway.")
    except Exception as e:
        print(f"    [UI] Warning: Could not push status: {e}")

if __name__ == "__main__":
    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["media.audio", "media.video"])
    client.listen(on_message)