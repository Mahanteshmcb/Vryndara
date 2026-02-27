import sys
import os
import asyncio
import logging
import grpc
import time
import json
from concurrent import futures
from threading import Thread  # NEW: For parallel processing

# --- PATH SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- KERNEL IMPORTS ---
from protos import vryndara_pb2, vryndara_pb2_grpc
from kernel.database import init_db, AsyncSessionLocal, EventLog
from agents.coder.code_generator import CoderAgent
from Vryndara_Core.services.engineering_service import EngineeringService
from sdk.python.vryndara.storage import StorageManager

# --- JARVIS VOICE IMPORTS ---
from Vryndara_Core.services.voice_engine import VoiceEngine
from Vryndara_Core.services.brain_service import BrainService
from Vryndara_Core.services.director_skill import DirectorSkill
from colorama import Fore, init

init(autoreset=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KERNEL] - %(message)s')

class VryndaraKernel(vryndara_pb2_grpc.KernelServicer):
    def __init__(self):
        self.message_queues = {}
        self.registry = {}
        self.response_futures = {} 

        # --- SERVICES ---
        self.storage = StorageManager(bucket_name="vryndara_output")
        self.engineer = EngineeringService(self.storage)
        
        # --- BRAIN (Shared) ---
        self.brain = BrainService() 
        self.director = DirectorSkill(self.brain)
        
        # --- CODER (Specialized) ---
        model_path = r"C:\Users\Mahantesh\DevelopmentProjects\VrindaAI\VrindaAI\llama.cpp\build\bin\Release\mistral.gguf"
        self.coder = CoderAgent(model_path)

    async def Register(self, request, context):
        logging.info(f"Registering Agent: {request.id}")
        self.registry[request.id] = request
        if request.id not in self.message_queues:
            self.message_queues[request.id] = asyncio.Queue()
        return vryndara_pb2.Ack(success=True)

    async def Publish(self, request, context):
        target = request.target_agent_id
        
        try:
            async with AsyncSessionLocal() as session:
                event = EventLog(
                    id=request.id, source=request.source_agent_id,
                    target=request.target_agent_id, type=request.type,
                    payload=request.payload, timestamp=request.timestamp
                )
                session.add(event)
                await session.commit()
        except Exception as e:
            logging.error(f"DB Write Failed: {e}")

        # This ensures the Bridge (UI-Gateway) receives the gesture data
        for agent_id, queue in self.message_queues.items():
            # We send to everyone who is NOT the source
            if agent_id != request.source_agent_id:
                await queue.put(request)

                
        if target == "ComputationalEngineer":
            logging.info(f"⚙️ Kernel Intercept: Engineering Task received: {request.payload}")
            try:
                loop = asyncio.get_running_loop()
                logging.info("🧠 Brain is thinking...")
                generated_code = await loop.run_in_executor(None, self.coder.generate_sdf_code, request.payload)
                full_code_context = f"from sdf import sphere, cylinder, union, difference, Z, slab, intersection, box, rounded_box, capsule, pi\n{generated_code}"
                logging.info("⚙️ Compiling Geometry...")
                result = await loop.run_in_executor(None, self.engineer.generate_sdf_from_code, full_code_context)
                return vryndara_pb2.Ack(success=True, error=json.dumps(result))
            except Exception as e:
                logging.error(f"❌ Engineering Task Failed: {e}")
                return vryndara_pb2.Ack(success=False, error=str(e))

        if request.type == "TASK_RESULT" and request.source_agent_id in self.response_futures:
            future = self.response_futures[request.source_agent_id]
            if not future.done():
                future.set_result(request.payload)

        if target in self.message_queues:
            await self.message_queues[target].put(request)
            return vryndara_pb2.Ack(success=True)
        elif target == "Kernel-Orchestrator":
            return vryndara_pb2.Ack(success=True)
        return vryndara_pb2.Ack(success=False, error="Target offline")

    async def Subscribe(self, request, context):
        agent_id = request.id
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = asyncio.Queue()
        queue = self.message_queues[agent_id]
        while True:
            yield await queue.get()

    async def ExecuteWorkflow(self, request, context):
        workflow_id = request.workflow_id
        logging.info(f"🚀 Starting Smart Workflow: {workflow_id}")
        sorted_steps = sorted(request.steps, key=lambda s: s.step_order)
        previous_step_result = "" 

        for step in sorted_steps:
            logging.info(f"▶️  Step {step.step_order}: Asking {step.agent_id}...")
            current_task = step.task_payload
            if previous_step_result:
                current_task += f"\n\n[CONTEXT FROM PREVIOUS AGENT]:\n{previous_step_result}"

            loop = asyncio.get_running_loop()
            result_future = loop.create_future()
            self.response_futures[step.agent_id] = result_future

            signal = vryndara_pb2.Signal(
                id=f"{workflow_id}-{step.step_order}", source_agent_id="Kernel-Orchestrator",
                target_agent_id=step.agent_id, type="TASK_REQUEST", payload=current_task, timestamp=int(time.time())
            )
            await self.Publish(signal, context)
            try:
                result_payload = await asyncio.wait_for(result_future, timeout=300.0)
                logging.info(f"✅ Step {step.step_order} Complete.")
                previous_step_result = result_payload 
            except asyncio.TimeoutError:
                logging.error(f"❌ Step {step.step_order} Timed Out!")
                previous_step_result = "" 
            finally:
                if step.agent_id in self.response_futures:
                    del self.response_futures[step.agent_id]

        logging.info(f"🏁 Workflow {workflow_id} Finished.")
        return vryndara_pb2.Ack(success=True, error=f"Completed: {workflow_id}")


# --- NEW: UDP SENSOR GATEWAY ---
def sensor_gateway_loop(kernel_instance, main_loop): # <--- ADD main_loop HERE
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 50052))
    print(f"{Fore.CYAN}📡 Kernel Sensor Gateway listening on UDP:50052")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            payload_str = data.decode('utf-8')
            logging.info(f"🦾 [VISION SENSOR INPUT]: {payload_str}")
            
            signal = vryndara_pb2.Signal(
                id=f"vision-{int(time.time())}",
                source_agent_id="Jarvis-Vision",
                target_agent_id="Kernel-Orchestrator",
                type="GESTURE_EVENT",
                payload=payload_str,
                timestamp=int(time.time())
            )
            
            # --- THE FIX: Thread-safe execution on the main loop ---
            asyncio.run_coroutine_threadsafe(kernel_instance.Publish(signal, None), main_loop)
            # -------------------------------------------------------

        except Exception as e:
            logging.error(f"Sensor Gateway Error: {e}")


# --- THE JARVIS LOOP (RUNS IN PARALLEL) ---
def jarvis_voice_loop(kernel_instance):
    print(f"{Fore.GREEN}🎙️  Initializing Voice Systems...")
    try:
        voice = VoiceEngine()
    except Exception as e:
        print(f"{Fore.RED}❌ Voice Init Failed: {e}")
        return

    brain = kernel_instance.brain 
    director = kernel_instance.director
    print(f"{Fore.GREEN}✅ Jarvis Voice Online. Speak now.")
    
    while True:
        try:
            # --- HYBRID MODE: KEYBOARD + SMART VOICE ---
            user_text = input(f"{Fore.CYAN}⌨️ Type a command (or press Enter for Voice): ")
            
            # 1. If you just hit Enter (empty string), turn on the Smart Mic
            if not user_text.strip():
                print(f"{Fore.MAGENTA}🎧 Turning on Microphone...")
                # I lowered the threshold to 0.005 so it picks up quiet voices!
                user_text = voice.listen(silence_limit=1.5, threshold=0.005)
                
            # If Whisper returns nothing, loop back
            if not user_text:
                continue

            # 2. SHUT DOWN
            if "shut down" in user_text.lower():
                voice.speak("Shutting down Vryndara systems.")
                os.system('taskkill /FI "WINDOWTITLE eq Vryndara_Vision*" /T /F >nul 2>&1')
                os._exit(0) 

            # 3. THE FIX: Check DEACTIVATE first!
            if "deactivate vision" in user_text.lower() or "turn off eyes" in user_text.lower():
                voice.speak("Deactivating optical sensors.")
                # Kill the terminal window
                os.system('taskkill /FI "WINDOWTITLE eq Vryndara_Vision*" /T /F >nul 2>&1')
                # Kill the OpenCV camera window specifically
                os.system('taskkill /FI "WINDOWTITLE eq Vryndara Vision Core*" /T /F >nul 2>&1')
                continue
            
            # 4. Then check ACTIVATE
            elif "activate vision" in user_text.lower() or "turn on eyes" in user_text.lower():
                voice.speak("Activating optical sensors.")
                print(f"{Fore.CYAN}🚀 Launching Vision Microservice...")
                import subprocess
                cmd = 'start "Vryndara_Vision" cmd.exe /c "conda activate vryndara-vision && python Vryndara_Core/services/vision_service.py"'
                subprocess.Popen(cmd, shell=True)
                continue 

            # 5. STANDARD SKILL ROUTING
            trigger_words = ["create", "make", "build", "generate", "render"]
            is_creative_task = any(word in user_text.lower() for word in trigger_words)
            
            if is_creative_task:
                print(f"{Fore.YELLOW}⚙️ Director Mode Active")
                response = director.create_manifest(user_text)
            else:
                print(f"{Fore.YELLOW}🧠 Chat Mode Active")
                response = brain.think(user_text)

            voice.speak(response)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Voice Loop Error: {e}")
            import time
            time.sleep(1)

# --- MAIN SERVER STARTUP ---
async def serve():
    await init_db()
    
    kernel_service = VryndaraKernel()
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    vryndara_pb2_grpc.add_KernelServicer_to_server(kernel_service, server)
    server.add_insecure_port('[::]:50051')
    
    logging.info("🚀 Vryndara Kernel (Neural & Voice) Starting...")
    await server.start()

    # --- GRAB THE MAIN LOOP ---
    main_loop = asyncio.get_running_loop()
    
    # Run the Voice Engine as a background daemon
    voice_thread = Thread(target=jarvis_voice_loop, args=(kernel_service,), daemon=True)
    voice_thread.start()

    # --- NEW: START SENSOR GATEWAY ---
    # --- PASS MAIN LOOP TO SENSOR GATEWAY ---
    sensor_thread = Thread(target=sensor_gateway_loop, args=(kernel_service, main_loop), daemon=True)
    sensor_thread.start()
    
    logging.info("✅ Kernel & Jarvis are Live.")
    await server.wait_for_termination()

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("\n🛑 Force Stopping Kernel...")
        # Clean up the camera window when you hit Ctrl+C
        import os
        os.system('taskkill /FI "WINDOWTITLE eq Vryndara_Vision*" /T /F >nul 2>&1')
        print("✅ Shutdown complete.")