import time
import uuid
import grpc
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- NEW IMPORT
from pydantic import BaseModel
from typing import Optional

# Clean Imports
from protos import vryndara_pb2, vryndara_pb2_grpc

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gateway")

app = FastAPI(title="Vryndara API Gateway", version="0.1.0")

# --- NEW: ENABLE CORS ---
# This tells the browser: "Allow requests from localhost:5173"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, we allow all origins. In prod, lock this down.
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)
# ------------------------

# --- Configuration ---
KERNEL_ADDRESS = "localhost:50051"

# --- Data Models ---
class TaskRequest(BaseModel):
    source_agent_id: str = "External-App"
    target_agent_id: str
    payload: str

class TaskResponse(BaseModel):
    message_id: str
    status: str
    timestamp: int

class WorkflowStepModel(BaseModel):
    agent_id: str
    task: str
    order: int

class WorkflowSubmit(BaseModel):
    steps: list[WorkflowStepModel]

# --- API Endpoints ---

@app.get("/")
def health_check():
    return {"status": "online", "system": "Vryndara OS"}

@app.post("/api/v1/task", response_model=TaskResponse)
def submit_task(task: TaskRequest):
    try:
        channel = grpc.insecure_channel(KERNEL_ADDRESS)
        stub = vryndara_pb2_grpc.KernelStub(channel)

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

        logger.info(f"Forwarding task to {task.target_agent_id}")
        ack = stub.Publish(signal)

        if not ack.success:
            raise HTTPException(status_code=500, detail=f"Kernel rejected task: {ack.error}")

        return TaskResponse(message_id=message_id, status="queued", timestamp=ts)

    except grpc.RpcError as e:
        logger.error(f"Kernel connection failed: {e}")
        raise HTTPException(status_code=503, detail="Vryndara Kernel is unreachable")

@app.post("/api/v1/workflow")
def run_workflow(workflow: WorkflowSubmit):
    try:
        channel = grpc.insecure_channel(KERNEL_ADDRESS)
        stub = vryndara_pb2_grpc.KernelStub(channel)

        proto_steps = []
        for s in workflow.steps:
            proto_steps.append(vryndara_pb2.WorkflowStep(
                agent_id=s.agent_id,
                task_payload=s.task,
                step_order=s.order
            ))

        req = vryndara_pb2.WorkflowRequest(
            workflow_id=str(uuid.uuid4()),
            steps=proto_steps
        )

        stub.ExecuteWorkflow(req)
        return {"status": "Workflow Started", "id": req.workflow_id}

    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e))