import asyncio
import logging
import grpc

# CLEAN IMPORT: directly from our new package
from protos import vryndara_pb2, vryndara_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KERNEL] - %(message)s')

class VryndaraKernel(vryndara_pb2_grpc.KernelServicer):
    # ... (Keep the rest of your class logic EXACTLY the same) ...
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
        logging.info(f"Routing msg: {request.source_agent_id} -> {target} [{request.type}]")
        if target in self.message_queues:
            await self.message_queues[target].put(request)
            return vryndara_pb2.Ack(success=True)
        else:
            return vryndara_pb2.Ack(success=False, error="Target offline")

    async def Subscribe(self, request, context):
        agent_id = request.id
        logging.info(f"Agent {agent_id} subscribed.")
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = asyncio.Queue()
        queue = self.message_queues[agent_id]
        while True:
            yield await queue.get()

async def serve():
    server = grpc.aio.server()
    vryndara_pb2_grpc.add_KernelServicer_to_server(VryndaraKernel(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Vryndara Kernel Ready (Clean Mode)...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())