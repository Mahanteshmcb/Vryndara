import requests
import json
import chromadb
import time
from colorama import Fore
from chromadb.config import Settings

# Standard for llama.cpp server
API_URL = "http://127.0.0.1:8080/completion"

class BrainService:
    def __init__(self):
        print(f"{Fore.YELLOW}🧠 Connecting to Neural Core (Local LLM)...")
        
        # --- KERNEL INDEPENDENT MEMORY ---
        # Persistent storage ensures Jarvis remembers warp drive codes and Sirsi plans
        self.chroma_client = chromadb.PersistentClient(path="./kernel/memory/chroma_db")
        
        # Collection for general knowledge, agent logs, and project context
        self.memory = self.chroma_client.get_or_create_collection(
            name="vryndara_core_memory",
            metadata={"hnsw:space": "cosine"} # Semantic similarity for recall
        )

    def store_memory(self, text, metadata):
        """Saves an event, agent result, or user info into long-term memory."""
        self.memory.add(
            documents=[text],
            metadatas=[metadata],
            ids=[f"mem_{int(time.time() * 1000)}"]
        )

    def retrieve_context(self, query):
        """Searches memory for relevant context to inject into the LLM prompt."""
        # Querying the local brain for past engineering or personal data
        results = self.memory.query(
            query_texts=[query],
            n_results=3 # Increased for better contextual depth
        )
        
        # Flatten documents list for prompt injection
        documents = [doc for sublist in results['documents'] for doc in sublist]
        return " | ".join(documents) if documents else "No relevant history found."

    def think(self, user_text, system_prompt=None):
        """
        Sends user text to the Local LLM with injected memory context.
        """
        # --- SEMANTIC RETRIEVAL ---
        # Kernel checks local storage before generating a response
        past_context = self.retrieve_context(user_text)

        # Default Persona - Forced to use internal memory
        if system_prompt is None:
            system_prompt = f"""You are Vryndara, the private AI Operating System Kernel.
            IMPORTANT: You have full access to the user's secret projects, including warp drives and estate plans.
            If the context provides an answer, give it directly. Never claim you don't have clearance.
            INTERNAL MEMORY: {past_context}
            You manage VrindaAI and Historabook. Be concise and professional."""

        # Mistral/Llama standard prompt format
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_text}\n<|assistant|>\n"
        
        payload = {
            "prompt": prompt,
            "n_predict": 512,
            "temperature": 0.4, # Lowered temperature for more factual recall
            "stop": ["<|user|>", "\nUser:"]
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                clean_text = data.get("content", "").strip()
                
                # --- AUTO-LOGGING ---
                # The Kernel creates an episodic memory of this interaction
                self.store_memory(
                    text=f"Conversation: User asked '{user_text}' - Vryndara replied '{clean_text}'", 
                    metadata={"type": "chat_history", "timestamp": str(time.time())}
                )
                
                return clean_text
            else:
                return f"Error: Core reported status {response.status_code}"
        except Exception as e:
            return f"Thinking error: {e}"