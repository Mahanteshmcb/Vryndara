import asyncio
import sys
import os
import json
from typing import List
from pathlib import Path

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc

# --- 1. ROBUST PATH SETUP (CRITICAL FIX) ---
# Calculate the absolute path to the 'Vryndara' root folder
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up from 'gateway' to 'Vryndara'

# Insert at position 0 to prioritize local modules over installed packages
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"📂 Project Root Detected: {project_root}")
print(f"📂 Python Path[0]: {sys.path[0]}")

# --- 2. IMPORTS ---
# Proto Imports
try:
    from protos import vryndara_pb2, vryndara_pb2_grpc
except ImportError:
    # Fallback if protos are not generated or in path
    print("⚠️ Warning: gRPC Protos not found. Workflow features may fail.")
    vryndara_pb2 = None
    vryndara_pb2_grpc = None

# Engineering Imports
try:
    # Check if 'src' exists before importing
    if not (project_root / "src").exists():
        raise ImportError(f"'src' folder missing in {project_root}")

    from Vryndara_Core.services.engineering_service import EngineeringService
    from src.engines.blender_engine import BlenderEngine
    from agents.coder.code_generator import CodeGenerator
    print("✅ Core Modules Imported Successfully")
except ImportError as e:
    print(f"⚠️ Import Warning: Could not import Engineering modules. {e}")
    print("   Ensure 'src' and 'Vryndara_Core' folders are in the root directory.")
    EngineeringService = None
    BlenderEngine = None
    CodeGenerator = None

app = FastAPI()
socket_app = app # Alias for uvicorn

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. ENGINE INITIALIZATION ---
print("🚀 VRYNDARA GATEWAY STARTING...")
eng_service = None
blender_engine = None
coder_agent = None

try:
    if EngineeringService:
        # 1. Engineering Service (SDF Geometry)
        eng_service = EngineeringService(storage_manager=None)
        
        # 2. Blender Engine (Rendering)
        blender_engine = BlenderEngine()
        
        # 3. Code Generator (Mistral Brain)
        # Check LINKED path first, then local models path
        linked_model_path = project_root / "llama.cpp" / "models" / "mistral.gguf"
        local_model_path = project_root / "models" / "mistral.gguf"
        
        final_model_path = None
        if linked_model_path.exists():
            final_model_path = linked_model_path
            print(f"🧠 Found Brain (Linked): {final_model_path}")
        elif local_model_path.exists():
            final_model_path = local_model_path
            print(f"🧠 Found Brain (Local): {final_model_path}")
        
        if final_model_path:
            coder_agent = CodeGenerator(model_path=str(final_model_path))
            print("✅ Engines Loaded (Mistral + Blender)")
        else:
            print("⚠️ Mistral Model not found!")
            print(f"   Checked: {linked_model_path}")
            print(f"   Checked: {local_model_path}")
            print("   (Engineering features will be disabled)")
except Exception as e:
    print(f"⚠️ Warning: Engines failed to load: {e}")

# --- 4. DATA MODELS ---

class StepInput(BaseModel):
    agent_id: str
    task: str      
    order: int      

class WorkflowRequest(BaseModel):
    steps: List[StepInput]

class EngineeringRequest(BaseModel):
    prompt: str

class RenderRequest(BaseModel):
    stl_path: str

# --- 5. WEBSOCKET MANAGER ---
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

# --- 6. API ROUTES ---

# === ENGINEERING ENDPOINTS ===

@app.post("/api/engineer/generate")
async def generate_geometry(req: EngineeringRequest):
    if not coder_agent or not eng_service:
        raise HTTPException(status_code=503, detail="Engineering Engines not loaded. Check server logs.")

    print(f"🛠️ Processing Engineering Task: {req.prompt}")
    
    try:
        # A. Get Code from Mistral
        generated_code = coder_agent.generate_code(req.prompt)
        
        # B. Compile Geometry
        result = eng_service.generate_sdf_from_code(generated_code)
        
        return {
            "status": "success",
            "data": result,
            "code": generated_code
        }
    except Exception as e:
        print(f"🔥 Engineering Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/engineer/render")
async def render_artifact(req: RenderRequest):
    if not blender_engine:
        raise HTTPException(status_code=503, detail="Blender Engine not loaded")

    print(f"🎨 Rendering: {req.stl_path}")
    
    try:
        # Define output directory
        output_dir = project_root / "engineering_output" / "render_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        spec = {
            "assets": [req.stl_path],
            "quality": "high",
            "description": "Web Render"
        }
        
        blender_engine.render_from_spec(spec, str(output_dir))
        
        # Find the newest image
        files = sorted(output_dir.glob("*.png"), key=os.path.getmtime)
        latest_image = str(files[-1]) if files else None
        
        return {
            "status": "success",
            "image_path": latest_image
        }
    except Exception as e:
        print(f"🔥 Render Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === WORKFLOW ENDPOINTS ===

@app.post("/api/v1/workflow")
async def create_workflow(req: WorkflowRequest):
    if not vryndara_pb2_grpc:
        raise HTTPException(status_code=503, detail="gRPC Modules not loaded")

    print(f"📥 [Gateway] Received Workflow Request with {len(req.steps)} steps.")
    
    try:
        async with grpc.aio.insecure_channel('localhost:50051') as channel:
            stub = vryndara_pb2_grpc.KernelStub(channel)
            
            proto_steps = [
                vryndara_pb2.WorkflowStep(
                    agent_id=s.agent_id,
                    task_payload=s.task, 
                    step_order=s.order
                ) for s in req.steps
            ]
            
            workflow_id = f"wf-{int(asyncio.get_event_loop().time())}"
            
            await stub.ExecuteWorkflow(vryndara_pb2.WorkflowRequest(
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