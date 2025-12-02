import asyncio
import logging
import grpc
from protos import vryndara_pb2, vryndara_pb2_grpc

# NEW: Import database functions
from kernel.database import init_db, AsyncSessionLocal, EventLog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KERNEL] - %(message)s')

class VryndaraKernel(vryndara_pb2_grpc.KernelServicer):
    def __init__(self):
        self.message_queues = {}
        self.registry = {}

    async def Register(self, request, context):
        logging.info(f"Registering Agent: {request.id}")
        self.registry[request.id] = request
        if request.id not in self.message_queues:
            self.message_queues[request.id] = asyncio.Queue()
        return vryndara_pb2.Ack(success=True)

    async def Publish(self, request, context):
        target = request.target_agent_id
        
        # --- NEW: PERSISTENCE LAYER ---
        # We save the message to Postgres BEFORE routing it
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
            logging.info(f"Saved & Routing: {request.source_agent_id} -> {target}")
        except Exception as e:
            logging.error(f"DB Write Failed: {e}")
        # ------------------------------

        if target in self.message_queues:
            await self.message_queues[target].put(request)
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
        Orchestrates a multi-step workflow.
        For Phase 1, we just fire the steps in order.
        """
        logging.info(f"Starting Workflow: {request.workflow_id} with {len(request.steps)} steps.")
        
        # Sort steps by order (1, 2, 3...)
        sorted_steps = sorted(request.steps, key=lambda s: s.step_order)

        for step in sorted_steps:
            logging.info(f"  -> Executing Step {step.step_order}: {step.agent_id}")
            
            # Construct a Signal for this step
            signal = vryndara_pb2.Signal(
                id=request.workflow_id + f"-{step.step_order}",
                source_agent_id="Kernel-Orchestrator",
                target_agent_id=step.agent_id,
                type="TASK_REQUEST",
                payload=step.task_payload,
                timestamp=0 # We'll fix timestamp later
            )

            # Re-use our own Publish logic to route it and save to DB
            # We call self.Publish directly!
            await self.Publish(signal, context)
            
            # Artificial delay so we can see it happening in the UI later
            await asyncio.sleep(1) 

        return vryndara_pb2.Ack(success=True)

async def serve():
    # 1. Initialize the Database Tables first
    await init_db()
    
    # 2. Start gRPC Server
    server = grpc.aio.server()
    vryndara_pb2_grpc.add_KernelServicer_to_server(VryndaraKernel(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Vryndara Kernel (With Memory) Ready...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())