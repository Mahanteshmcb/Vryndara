import asyncio
import logging
import grpc
import time
from protos import vryndara_pb2, vryndara_pb2_grpc

# Import database functions
from kernel.database import init_db, AsyncSessionLocal, EventLog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KERNEL] - %(message)s')

class VryndaraKernel(vryndara_pb2_grpc.KernelServicer):
    def __init__(self):
        self.message_queues = {}
        self.registry = {}
        # NEW: A place to store "waiting" tickets for workflows
        self.response_futures = {} 

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
            # logging.info(f"Saved: {request.source_agent_id} -> {target} [{request.type}]")
        except Exception as e:
            logging.error(f"DB Write Failed: {e}")

        # --- 2. WORKFLOW INTERCEPTION (The "Listener") ---
        # If an agent is sending a RESULT, check if the Workflow is waiting for it.
        if request.type == "TASK_RESULT":
            # Check if we are waiting for this agent
            if request.source_agent_id in self.response_futures:
                logging.info(f"⚡ Captured Result from {request.source_agent_id} for Workflow.")
                future = self.response_futures[request.source_agent_id]
                if not future.done():
                    future.set_result(request.payload)
                # We still allow the message to route normally below

        # --- 3. STANDARD ROUTING ---
        if target in self.message_queues:
            await self.message_queues[target].put(request)
            return vryndara_pb2.Ack(success=True)
        elif target == "Kernel-Orchestrator":
            # Just absorb messages meant for Kernel
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
        """
        Smart Orchestrator: Executes steps sequentially and passes data (Context).
        """
        workflow_id = request.workflow_id
        logging.info(f"🚀 Starting Smart Workflow: {workflow_id}")
        
        sorted_steps = sorted(request.steps, key=lambda s: s.step_order)
        
        # --- NEW: THE BATON (Context) ---
        previous_step_result = "" 

        for step in sorted_steps:
            logging.info(f"▶️  Step {step.step_order}: Asking {step.agent_id}...")
            
            # 1. Inject Context (if available)
            current_task = step.task_payload
            if previous_step_result:
                current_task += f"\n\n[CONTEXT FROM PREVIOUS AGENT]:\n{previous_step_result}"
                logging.info(f"   (Injected {len(previous_step_result)} chars of context)")

            # 2. Create a Future to wait for the result
            loop = asyncio.get_running_loop()
            result_future = loop.create_future()
            self.response_futures[step.agent_id] = result_future

            # 3. Send the Task
            signal = vryndara_pb2.Signal(
                id=f"{workflow_id}-{step.step_order}",
                source_agent_id="Kernel-Orchestrator",
                target_agent_id=step.agent_id,
                type="TASK_REQUEST",
                payload=current_task,
                timestamp=int(time.time())
            )
            await self.Publish(signal, context)
            
            # 4. WAIT for the Agent to finish (Blocking Wait)
            try:
                # Wait up to 60 seconds for the agent to reply
                result_payload = await asyncio.wait_for(result_future, timeout=60.0)
                
                logging.info(f"✅ Step {step.step_order} Complete.")
                previous_step_result = result_payload # <--- UPDATE THE BATON
                
            except asyncio.TimeoutError:
                logging.error(f"❌ Step {step.step_order} Timed Out! (Agent {step.agent_id} did not reply)")
                previous_step_result = "" # Reset chain on failure
            finally:
                # Clean up the future
                if step.agent_id in self.response_futures:
                    del self.response_futures[step.agent_id]

        logging.info(f"🏁 Workflow {workflow_id} Finished.")
        return vryndara_pb2.WorkflowResponse(status="COMPLETED", workflow_id=workflow_id)

async def serve():
    await init_db()
    server = grpc.aio.server()
    vryndara_pb2_grpc.add_KernelServicer_to_server(VryndaraKernel(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Vryndara Kernel (With Smart Handoffs) Ready...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())