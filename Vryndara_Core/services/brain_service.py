import requests
import json
from colorama import Fore

# We assume a local LLM server is running on port 8080 (Standard for llama.cpp)
API_URL = "http://localhost:8080/completion"

class BrainService:
    def __init__(self):
        print(f"{Fore.YELLOW}🧠 Connecting to Neural Core (Local LLM)...")

    # Change the definition of think() to this:
    def think(self, user_text, system_prompt=None):
        """
        Sends user text to the Local LLM. 
        Allows custom System Prompts for different skills (Director vs Chat).
        """
        # Default Chat Persona
        if system_prompt is None:
            system_prompt = """You are Vryndara, an advanced AI Operating System. 
            You are helpful, concise, and robotic but friendly.
            Keep answers under 2 sentences for voice output."""

        # Construct the prompt format (Mistral/Llama standard)
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_text}\n<|assistant|>\n"
        
        payload = {
            "prompt": prompt,
            "n_predict": 512,  # Increased for coding tasks
            "temperature": 0.7,
            "stop": ["<|user|>", "\nUser:"]
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                raw_text = data.get("content", "").strip()
                # Clean up tags
                clean_text = raw_text.split("<|system|>")[0].strip()
                return clean_text
            else:
                return f"Error: Core reported status {response.status_code}"
        except Exception as e:
            return f"Thinking error: {e}"