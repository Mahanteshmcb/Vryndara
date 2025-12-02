import time
import ollama  # <--- The new library
from sdk.python.vryndara.client import AgentClient

AGENT_ID = "coder-alpha"
# Use the model you already downloaded. 
# You can swap this string to "qwencoder" later if you want.
MODEL_NAME = "llama3.1:8b" 

def generate_code(prompt):
    """
    Sends the prompt to your local Llama 3.1 model.
    """
    print(f"    [Brain] Thinking with {MODEL_NAME}...")
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'system',
                'content': 'You are an expert Python coding agent. Output ONLY valid Python code. No markdown, no conversational filler.'
            },
            {
                'role': 'user',
                'content': prompt
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"# Error generating code: {str(e)}"

def on_message(signal):
    print(f"\n>>> [RECEIVED] {signal.type} from {signal.source_agent_id}")
    
    if signal.type == "TASK_REQUEST":
        user_prompt = signal.payload
        print(f"    [Task] {user_prompt}")
        
        # --- CALL THE LLM ---
        start_ts = time.time()
        generated_code = generate_code(user_prompt)
        duration = round(time.time() - start_ts, 2)
        # ADD THIS LINE TO DEBUG:
        print(f"    [DEBUG] Content: {generated_code[:100]}...")
        # --------------------

        print(f"    [Done] Generated in {duration}s. Sending reply...")
        
        client.send(
            target_id=signal.source_agent_id,
            msg_type="TASK_RESULT",
            payload=generated_code
        )

if __name__ == "__main__":
    # Safety Check: Is Ollama actually running?
    try:
        ollama.list()
        print(f"✅ Connected to Ollama. Using model: {MODEL_NAME}")
    except:
        print("❌ Error: Ollama is not running! Please open the Ollama app.")
        exit(1)

    client = AgentClient(AGENT_ID, kernel_address="localhost:50051")
    client.register(["python.generation", "ai.local"])
    client.listen(on_message)