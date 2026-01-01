import sys
import os

# --- FIX: Add Project Root to Path ---
# This allows imports from 'Vryndara_Core' and 'protos' to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import asyncio
import logging
import grpc
import time
from concurrent import futures
from protos import vryndara_pb2, vryndara_pb2_grpc

# --- AGENT IMPORTS ---
from agents.coder.code_generator import CoderAgent

# Import database functions
from kernel.database import init_db, AsyncSessionLocal, EventLog

# --- IMPORTS FOR ENGINEERING MODULE ---
from Vryndara_Core.services.engineering_service import EngineeringService
from sdk.python.vryndara.storage import StorageManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KERNEL] - %(message)s')

class VryndaraKernel(vryndara_pb2_grpc.KernelServicer):
    def __init__(self):
        self.message_queues = {}
        self.registry = {}
        self.response_futures = {} 

        # --- INITIALIZE SERVICES ---
        self.storage = StorageManager(bucket_name="vryndara_output")
        self.engineer = EngineeringService(self.storage)
        
        # --- INITIALIZE AI BRAIN (MISTRAL) ---
        # We use a raw string (r"...") to safely handle Windows backslashes
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
        
        # --- 1. PERSISTENCE LAYER ---
        try:
            async with AsyncSessionLocal() as session:
                event = EventLog(
                    id=request.id,
                    source=request.source_agent_id,
                    target=request.target_agent_id,
                    type=request.type,
                    payload=request.payload,
                    timestamp=request.timestamp
                )
                session.add(event)
                await session.commit()
        except Exception as e:
            logging.error(f"DB Write Failed: {e}")

        # --- 2. ENGINEERING MODULE (NEURAL LINK) ---
        if target == "ComputationalEngineer":
            logging.info(f"⚙️ Kernel Intercept: Engineering Task received: {request.payload}")
            
            try:
                loop = asyncio.get_running_loop()

                # STEP A: AI GENERATION (Run in Thread to avoid blocking server)
                # The Coder Agent uses Mistral to write the Python SDF code
                logging.info("🧠 Brain is thinking...")
                generated_code = await loop.run_in_executor(
                    None, 
                    self.coder.generate_sdf_code, 
                    request.payload
                )

                # STEP B: PREPARE CONTEXT
                # We inject the necessary imports so the AI code can run
                full_code_context = f"""
from sdf import sphere, cylinder, union, difference, Z, slab, intersection, box, rounded_box, capsule, pi
{generated_code}
"""
                
                # STEP C: GEOMETRY COMPILATION (Run in Thread)
                # The Engineering Service executes the code to create STLs and Blueprints
                logging.info("⚙️ Compiling Geometry...")
                result = await loop.run_in_executor(
                    None, 
                    self.engineer.generate_sdf_from_code, 
                    full_code_context
                )
                
                logging.info(f"✅ Engineering Artifacts Generated: {result}")
                
                # Return the JSON result to the client
                return vryndara_pb2.Ack(success=True, error=json.dumps(result))
                
            except Exception as e:
                logging.error(f"❌ Engineering Task Failed: {e}")
                return vryndara_pb2.Ack(success=False, error=str(e))

        # --- 3. WORKFLOW INTERCEPTION ---
        if request.type == "TASK_RESULT":
            if request.source_agent_id in self.response_futures:
                logging.info(f"⚡ Captured Result from {request.source_agent_id} for Workflow.")
                future = self.response_futures[request.source_agent_id]
                if not future.done():
                    future.set_result(request.payload)

        # --- 4. STANDARD ROUTING ---
        if target in self.message_queues:
            await self.message_queues[target].put(request)
            return vryndara_pb2.Ack(success=True)
        elif target == "Kernel-Orchestrator":
            return vryndara_pb2.Ack(success=True)
        else:
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

async def serve():
    await init_db()
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    vryndara_pb2_grpc.add_KernelServicer_to_server(VryndaraKernel(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Vryndara Kernel (With Mistral Brain) Ready...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(serve())