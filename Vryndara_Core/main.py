import sys
from services.voice_engine import VoiceEngine
from services.brain_service import BrainService
from services.director_skill import DirectorSkill # <--- NEW IMPORT
from colorama import Fore, Style, init

init(autoreset=True)

def main():
    print(f"{Fore.GREEN}============================================")
    print(f"{Fore.GREEN}   🧠 VRYNDARA OS (Kernel v0.4) - ONLINE    ")
    print(f"{Fore.GREEN}============================================")
    
    # Initialize Services
    voice = VoiceEngine()
    brain = BrainService()
    director = DirectorSkill(brain) # <--- NEW INIT (Pass brain to director)
    
    print(f"{Fore.GREEN}✅ System Ready. Waiting for input...")
    
    while True:
        # A. Listen
        user_text = voice.listen(duration=5)
        
        if not user_text:
            continue
            
        # Exit Command
        if "shut down" in user_text.lower():
            voice.speak("Shutting down systems. Goodbye.")
            break
            
        # B. Decide Skill (Chat vs Director)
        # Simple keyword detection for now
        trigger_words = ["create", "make", "build", "generate", "render"]
        is_creative_task = any(word in user_text.lower() for word in trigger_words)
        
        if is_creative_task:
            print(f"{Fore.YELLOW}⚙️ Routing to Director Skill...")
            response = director.create_manifest(user_text)
        else:
            print(f"{Fore.YELLOW}🧠 Routing to Chat Core...")
            response = brain.think(user_text) # Uses default chat prompt
        
        # C. Speak Result
        voice.speak(response)

if __name__ == "__main__":
    main()