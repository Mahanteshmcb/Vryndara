import grpc
import time
import uuid
# CLEAN IMPORT
from protos import vryndara_pb2, vryndara_pb2_grpc

class AgentClient:
    # ... (Keep the rest of your logic same) ...
    def __init__(self, agent_id, kernel_address='localhost:50051'):
        self.agent_id = agent_id
        self.channel = grpc.insecure_channel(kernel_address)
        self.stub = vryndara_pb2_grpc.KernelStub(self.channel)

    def register(self, capabilities):
        info = vryndara_pb2.AgentInfo(id=self.agent_id, capabilities=capabilities)
        self.stub.Register(info)
        print(f"[{self.agent_id}] Registered.")

    def send(self, target_id, msg_type, payload):
        signal = vryndara_pb2.Signal(
            id=str(uuid.uuid4()), source_agent_id=self.agent_id,
            target_agent_id=target_id, type=msg_type, payload=payload
        )
        self.stub.Publish(signal)

    def listen(self, callback):
        print(f"[{self.agent_id}] Listening...")
        info = vryndara_pb2.AgentInfo(id=self.agent_id)
        for signal in self.stub.Subscribe(info):
            callback(signal)