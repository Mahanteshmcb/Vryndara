import time
import uuid
import grpc
import logging
import socketio # <--- NEW
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Clean Imports
from protos import vryndara_pb2, vryndara_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gateway")

# --- SOCKET.IO SETUP ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI(title="Vryndara API Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Wrap FastAPI with SocketIO
socket_app = socketio.ASGIApp(sio, app)
# -----------------------

KERNEL_ADDRESS = "localhost:50051"

# --- Data Models ---
class WorkflowStepModel(BaseModel):
    agent_id: str
    task: str
    order: int

class WorkflowSubmit(BaseModel):
    steps: list[WorkflowStepModel]

# --- API Endpoints ---

@app.get("/")
def health_check():
    return {"status": "online"}

@app.post("/api/v1/workflow")
async def run_workflow(workflow: WorkflowSubmit):
    try:
        channel = grpc.insecure_channel(KERNEL_ADDRESS)
        stub = vryndara_pb2_grpc.KernelStub(channel)

        workflow_id = str(uuid.uuid4())
        proto_steps = []
        
        for s in workflow.steps:
            proto_steps.append(vryndara_pb2.WorkflowStep(
                agent_id=s.agent_id,
                task_payload=s.task,
                step_order=s.order
            ))

        req = vryndara_pb2.WorkflowRequest(
            workflow_id=workflow_id,
            steps=proto_steps
        )

        stub.ExecuteWorkflow(req)

        # --- NEW: Notify UI that we started ---
        await sio.emit('workflow_status', {
            'workflow_id': workflow_id,
            'status': 'STARTED',
            'step': 0
        })
        
        return {"status": "Workflow Started", "id": workflow_id}

    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: Webhook for Agents to report progress ---
class ProgressUpdate(BaseModel):
    workflow_id: str
    agent_id: str
    status: str # "COMPLETED"
    result_url: str = None

@app.post("/api/v1/progress")
async def report_progress(update: ProgressUpdate):
    """Agents call this when they finish a job."""
    logger.info(f"Progress Update: {update.agent_id} -> {update.status}")
    
    # Push event to React UI instantly
    await sio.emit('node_update', {
        'agent_id': update.agent_id,
        'status': 'COMPLETED',
        'url': update.result_url
    })
    return {"ok": True}