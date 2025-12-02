import time
import uuid
import grpc
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Clean Imports from your package
from protos import vryndara_pb2, vryndara_pb2_grpc

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gateway")

app = FastAPI(title="Vryndara API Gateway", version="0.1.0")

# --- Configuration ---
KERNEL_ADDRESS = "localhost:50051"

# --- Data Models (JSON Schema) ---
class TaskRequest(BaseModel):
    source_agent_id: str = "External-App"
    target_agent_id: str
    payload: str

class TaskResponse(BaseModel):
    message_id: str
    status: str
    timestamp: int

# --- API Endpoints ---

@app.get("/")
def health_check():
    """Check if the Gateway is running."""
    return {"status": "online", "system": "Vryndara OS"}

@app.post("/api/v1/task", response_model=TaskResponse)
def submit_task(task: TaskRequest):
    """
    The main door: External apps send tasks here.
    The Gateway forwards them to the Kernel via gRPC.
    """
    try:
        # 1. Open gRPC Connection to Kernel
        channel = grpc.insecure_channel(KERNEL_ADDRESS)
        stub = vryndara_pb2_grpc.KernelStub(channel)

        # 2. Convert JSON -> gRPC Signal
        message_id = str(uuid.uuid4())
        ts = int(time.time())
        
        signal = vryndara_pb2.Signal(
            id=message_id,
            source_agent_id=task.source_agent_id,
            target_agent_id=task.target_agent_id,
            type="TASK_REQUEST",
            payload=task.payload,
            timestamp=ts
        )

        # 3. Send to Kernel (Fire and Forget)
        logger.info(f"Forwarding task to {task.target_agent_id}")
        ack = stub.Publish(signal)

        if not ack.success:
            raise HTTPException(status_code=500, detail=f"Kernel rejected task: {ack.error}")

        return TaskResponse(message_id=message_id, status="queued", timestamp=ts)

    except grpc.RpcError as e:
        logger.error(f"Kernel connection failed: {e}")
        raise HTTPException(status_code=503, detail="Vryndara Kernel is unreachable")