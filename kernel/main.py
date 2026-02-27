import sys
import os
import asyncio
import logging
import grpc
import time
import json
from concurrent import futures
from threading import Thread

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
        
        # --- BRAIN (Shared with ChromaDB Memory) ---
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
        
        # 1. BROADCAST: Send to all subscribers (UI Bridge, etc.)
        for agent_id, queue in self.message_queues.items():
            if agent_id != request.source_agent_id:
                await queue.put(request)

        # 2. PERSISTENCE: Log to SQLite Event Database
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

        # 3. KERNEL INTERCEPTS
        if target == "ComputationalEngineer":
            logging.info(f"⚙️ Engineering Task received: {request.payload}")
            try:
                loop = asyncio.get_running_loop()
                # Notify UI that Brain is working
                thinking_signal = vryndara_pb2.Signal(
                    id=f"eng-{int(time.time())}",
                    type="MEMORY_RETRIEVAL", 
                    payload="{}",
                    source_agent_id="Kernel-Orchestrator",
                    target_agent_id="UI-Gateway"
                )
                await self.Publish(thinking_signal, context)

                generated_code = await loop.run_in_executor(None, self.coder.generate_sdf_code, request.payload)
                full_code_context = f"from sdf import sphere, cylinder, union, difference, Z, slab, intersection, box, rounded_box, capsule, pi\n{generated_code}"
                
                result = await loop.run_in_executor(None, self.engineer.generate_sdf_from_code, full_code_context)
                self.brain.store_memory(f"Generated SDF code for: {request.payload}", {"agent": "CoderAgent"})
                
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
        
        return vryndara_pb2.Ack(success=True)

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
            logging.info(f"▶️ Step {step.step_order}: Asking {step.agent_id}...")
            
            relevant_context = self.brain.retrieve_context(step.task_payload)
            current_task = f"[MEMORY CONTEXT]: {relevant_context}\n\n[TASK]: {step.task_payload}"
            
            if previous_step_result:
                current_task += f"\n\n[PREVIOUS RESULT]:\n{previous_step_result}"

            loop = asyncio.get_running_loop()
            result_future = loop.create_future()
            self.response_futures[step.agent_id] = result_future

            signal = vryndara_pb2.Signal(
                id=f"{workflow_id}-{step.step_order}", 
                source_agent_id="Kernel-Orchestrator",
                target_agent_id=step.agent_id, 
                type="TASK_REQUEST", 
                payload=current_task, 
                timestamp=int(time.time())
            )
            await self.Publish(signal, context)
            
            try:
                result_payload = await asyncio.wait_for(result_future, timeout=300.0)
                self.brain.store_memory(
                    text=f"Step {step.step_order} Result: {result_payload}",
                    metadata={"workflow": workflow_id, "agent": step.agent_id}
                )
                previous_step_result = result_payload 
            except asyncio.TimeoutError:
                logging.error(f"❌ Step {step.step_order} Timed Out!")
            finally:
                if step.agent_id in self.response_futures:
                    del self.response_futures[step.agent_id]

        return vryndara_pb2.Ack(success=True)

# --- SENSOR GATEWAY ---
def sensor_gateway_loop(kernel_instance, main_loop):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 50052))
    print(f"{Fore.CYAN}📡 Kernel Sensor Gateway listening on UDP:50052")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            payload_str = data.decode('utf-8')
            
            signal = vryndara_pb2.Signal(
                id=f"vision-{int(time.time())}",
                source_agent_id="Jarvis-Vision",
                target_agent_id="Kernel-Orchestrator",
                type="GESTURE_EVENT",
                payload=payload_str,
                timestamp=int(time.time())
            )
            asyncio.run_coroutine_threadsafe(kernel_instance.Publish(signal, None), main_loop)
        except Exception as e:
            logging.error(f"Sensor Error: {e}")

# --- VOICE LOOP ---
def jarvis_voice_loop(kernel_instance, main_loop):
    print(f"{Fore.GREEN}🎙️ Initializing Voice Systems...")
    voice = VoiceEngine()
    brain = kernel_instance.brain 
    
    while True:
        try:
            user_text = input(f"{Fore.CYAN}⌨️ Command: ")
            if not user_text.strip():
                user_text = voice.listen()
            
            if not user_text: continue

            # Vision Controls
            if "activate vision" in user_text.lower():
                import subprocess
                subprocess.Popen('start cmd.exe /c "conda activate vryndara && python Vryndara_Core/services/vision_service.py"', shell=True)
                voice.speak("Eyes online.")
                continue

            # --- THINKING SIGNAL BROADCAST ---
            thinking_signal = vryndara_pb2.Signal(
                id=f"voice-think-{int(time.time())}",
                source_agent_id="Kernel-Orchestrator",
                target_agent_id="UI-Gateway",
                type="MEMORY_RETRIEVAL", # Triggers Purple Color
                payload=json.dumps({"status": "thinking"}),
                timestamp=int(time.time())
            )
            asyncio.run_coroutine_threadsafe(kernel_instance.Publish(thinking_signal, None), main_loop)

            # Chat Logic (Heavy processing)
            response = brain.think(user_text)

            # --- IDLE SIGNAL BROADCAST ---
            idle_signal = vryndara_pb2.Signal(
                id=f"voice-idle-{int(time.time())}",
                source_agent_id="Kernel-Orchestrator",
                target_agent_id="UI-Gateway",
                type="IDLE", # Returns to Blue
                payload="{}",
                timestamp=int(time.time())
            )
            asyncio.run_coroutine_threadsafe(kernel_instance.Publish(idle_signal, None), main_loop)

            voice.speak(response)
            
        except Exception as e:
            logging.error(f"Voice Error: {e}")

# --- STARTUP ---
async def serve():
    await init_db()
    kernel_service = VryndaraKernel()
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    vryndara_pb2_grpc.add_KernelServicer_to_server(kernel_service, server)
    server.add_insecure_port('[::]:50051')
    
    await server.start()
    main_loop = asyncio.get_running_loop()
    
    # Pass main_loop to threads for safe cross-thread async calls
    Thread(target=jarvis_voice_loop, args=(kernel_service, main_loop), daemon=True).start()
    Thread(target=sensor_gateway_loop, args=(kernel_service, main_loop), daemon=True).start()
    
    logging.info("✅ Kernel & Jarvis are Live.")
    await server.wait_for_termination()

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(serve())