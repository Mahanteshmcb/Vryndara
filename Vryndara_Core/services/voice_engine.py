import os
import sys
import time
import queue
import logging
import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from faster_whisper import WhisperModel
from colorama import Fore, Style, init

# Initialize colors
init(autoreset=True)

# Configuration
MODEL_PATH = os.path.join("models", "faster-whisper-small")
PIPER_MODEL = os.path.join("models", "piper-voice-ryan", "en_US-ryan-medium.onnx")
PIPER_BINARY = "piper.exe" # Ensure this is in your PATH or provide full path
SAMPLE_RATE = 16000
CHANNELS = 1

class VoiceEngine:
    def __init__(self):
        print(f"{Fore.CYAN}🎧 Initializing Ears (Whisper)...")
        
        # Check if model exists
        if not os.path.exists(MODEL_PATH):
            print(f"{Fore.RED}❌ Error: Whisper model not found at {MODEL_PATH}")
            self.model = None
        else:
            try:
                # Load the local model (CPU for compatibility, CUDA if you have it)
                device = "cuda" if os.environ.get("USE_GPU") == "true" else "cpu"
                self.model = WhisperModel(MODEL_PATH, device=device, compute_type="int8")
                print(f"{Fore.GREEN}✅ Ears Ready.")
            except Exception as e:
                print(f"{Fore.RED}❌ Failed to load Whisper: {e}")
                self.model = None

    def listen(self, silence_limit=1.5, threshold=0.015):
        """
        Smart Listening: Waits for you to speak, and stops when you are quiet.
        """
        if not self.model:
            return input(f"{Fore.YELLOW}🎤 (Text Mode) Enter command: {Style.RESET_ALL}")

        print(f"{Fore.CYAN}🎤 Waiting for your voice... (Speak whenever you are ready)")
        
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(indata.copy())

        audio_buffer = []
        is_speaking = False
        silence_time = 0

        # A small pre-buffer so we don't cut off the first letter of your sentence
        pre_buffer = []

        try:
            # Forcing channels=1 often fixes Windows laptop microphone issues!
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
                print(f"{Fore.CYAN}🎤 Mic is LIVE. Speak to see the volume meter move...")
                while True:
                    chunk = q.get()
                    
                    # Calculate the volume level
                    rms = np.sqrt(np.mean(chunk**2))

                    # --- THE LIVE VOLUME METER ---
                    if not is_speaking:
                        # Print a visual bar so you can see your mic levels
                        level = int(rms * 1000)  # Scale up for visibility
                        meter = "█" * min(level, 30)
                        print(f"\rVolume: [{meter.ljust(30)}] (Level: {rms:.5f})", end="")

                    # Using an ultra-low threshold of 0.008 to detect even the slightest voice (like a whisper)
                    if rms > 0.008:
                        if not is_speaking:
                            print(f"\n{Fore.GREEN}⏺️ Voice detected! Recording...")
                            is_speaking = True
                        silence_time = 0
                    
                    if is_speaking:
                        audio_buffer.append(chunk)
                        if rms <= 0.006:
                            silence_time += len(chunk) / SAMPLE_RATE
                            if silence_time > silence_limit:
                                break
                    else:
                        pre_buffer.append(chunk)
                        if len(pre_buffer) > 10:
                            pre_buffer.pop(0)

            print(f"{Fore.CYAN}⏳ Transcribing...")
            audio_data = np.concatenate(audio_buffer, axis=0)
            
            # Save the file for Whisper
            temp_wav = "temp_input.wav"
            wav.write(temp_wav, SAMPLE_RATE, audio_data)
            
            # Transcribe
            segments, _ = self.model.transcribe(temp_wav, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()
            
            # Ignore weird Whisper hallucinations (like the Georgian text from earlier)
            if len(text) < 2:
                return ""
                
            print(f"{Fore.MAGENTA}🗣️ You said: {text}")
            return text
            
        except Exception as e:
            print(f"{Fore.RED}❌ Recording Error: {e}")
            return ""

    def speak(self, text):
        """
        Uses Piper TTS with the correct subfolder path.
        """
        print(f"{Fore.BLUE}🤖 Vryndara: {text}")

        base_dir = os.getcwd()
        
        # FIX: Point to the 'piper' subfolder
        piper_exe = os.path.join(base_dir, "piper", "piper.exe")
        
        model_path = os.path.join(base_dir, "models", "piper-voice-ryan", "en_US-ryan-medium.onnx")
        output_file = os.path.join(base_dir, "response.wav")

        if not os.path.exists(piper_exe):
            print(f"{Fore.RED}❌ Critical: piper.exe not found at: {piper_exe}")
            return

        try:
            cmd = [piper_exe, "--model", model_path, "--output_file", output_file]
            
            # Run Piper
            process = subprocess.run(cmd, input=text.encode('utf-8'), capture_output=True)
            
            if process.returncode != 0:
                # Print the error so we know if espeak-data is missing
                print(f"{Fore.RED}❌ Piper Error: {process.stderr.decode('utf-8', errors='ignore')}")
                return

            # Play Audio
            if os.path.exists(output_file):
                fs, data = wav.read(output_file)

                # SoundDevice hates int64. We convert to int16 (standard audio).
                if data.dtype != np.int16:
                    data = data.astype(np.int16)
                # -----------------------------------------

                sd.play(data, fs)
                sd.wait()

        except Exception as e:
            print(f"{Fore.RED}❌ Speech Error: {e}")

if __name__ == "__main__":
    # Test Loop
    bot = VoiceEngine()
    while True:
        user_input = bot.listen(duration=4) # Listen for 4 seconds
        if "exit" in user_input.lower():
            break
        if user_input:
            bot.speak(f"I heard you say: {user_input}")