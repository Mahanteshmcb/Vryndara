import asyncio
import json
import grpc
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from protos import vryndara_pb2, vryndara_pb2_grpc

class KernelBridge:
    def __init__(self):
        self.channel = None
        self.stub = None
        self.active_connections = []

    async def stream_from_kernel(self):
        # Initialize channel INSIDE the async loop
        self.channel = grpc.aio.insecure_channel('localhost:50051')
        self.stub = vryndara_pb2_grpc.KernelStub(self.channel)
        
        print("🔗 Bridge successfully connected to gRPC Kernel.")
        agent_info = vryndara_pb2.AgentInfo(id="UI-Gateway", capabilities=["DISPLAY"])
        
        try:
            async for signal in self.stub.Subscribe(agent_info):
                payload = {
                    "type": signal.type,
                    "data": json.loads(signal.payload),
                    "timestamp": signal.timestamp
                }
                # Clean up closed connections while broadcasting
                for connection in self.active_connections[:]:
                    try:
                        await connection.send_text(json.dumps(payload))
                    except:
                        self.active_connections.remove(connection)
        except Exception as e:
            print(f"❌ Kernel Stream Error: {e}")

bridge = KernelBridge()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs exactly when the server starts
    task = asyncio.create_task(bridge.stream_from_kernel())
    yield
    # This runs when the server stops
    if bridge.channel:
        await bridge.channel.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    bridge.active_connections.append(websocket)
    print(f"🌐 New Browser Connection: {websocket.client}")
    try:
        while True:
            await websocket.receive_text()
    except:
        if websocket in bridge.active_connections:
            bridge.active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    # Changed port to 8888 to avoid Windows permission/usage conflicts
    uvicorn.run(app, host="127.0.0.1", port=8888)