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