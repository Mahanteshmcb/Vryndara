import asyncio
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import grpc
import sys
import os
import json

# Fix imports for Protos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from protos import vryndara_pb2, vryndara_pb2_grpc

app = FastAPI()
socket_app = app # Alias for uvicorn

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. DATA MODELS (Matches vryndara_bridge.py) ---
class StepInput(BaseModel):
    agent_id: str
    task: str       # Bridge sends "task"
    order: int      # Bridge sends "order"

class WorkflowRequest(BaseModel):
    steps: List[StepInput]

# --- 2. WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# --- 3. API ROUTES ---
@app.post("/api/v1/workflow")
async def create_workflow(req: WorkflowRequest):
    """
    Receives JSON from Historabook -> Converts to gRPC -> Sends to Kernel
    """
    print(f"📥 [Gateway] Received Workflow Request with {len(req.steps)} steps.")
    
    try:
        # Connect to Kernel
        async with grpc.aio.insecure_channel('localhost:50051') as channel:
            stub = vryndara_pb2_grpc.KernelStub(channel)
            
            # Map JSON to Protobuf
            # IMPORTANT: Mapping 'task' (JSON) to 'task_payload' (gRPC)
            proto_steps = [
                vryndara_pb2.WorkflowStep(
                    agent_id=s.agent_id,
                    task_payload=s.task, 
                    step_order=s.order
                ) for s in req.steps
            ]
            
            workflow_id = f"wf-{int(asyncio.get_event_loop().time())}"
            
            # Call Kernel
            response = await stub.ExecuteWorkflow(vryndara_pb2.WorkflowRequest(
                workflow_id=workflow_id,
                steps=proto_steps
            ))
            
            return {"status": "started", "id": workflow_id}

    except grpc.RpcError as e:
        print(f"🔥 [Gateway] gRPC Error: {e}")
        raise HTTPException(status_code=500, detail=f"Kernel Connection Failed: {e.details()}")
    except Exception as e:
        print(f"🔥 [Gateway] Internal Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/progress")
async def update_progress(data: dict):
    """
    Agents call this to update the UI
    """
    print(f"🔄 [Gateway] Progress Update: {data.get('agent_id')} - {data.get('status')}")
    await manager.broadcast(data)
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)