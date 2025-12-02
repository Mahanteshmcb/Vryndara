import grpc
import time
import uuid

# --- NEW CLEAN IMPORT ---
# We now import from the 'protos' package we created
from protos import vryndara_pb2, vryndara_pb2_grpc
# ------------------------

def run():
    # Connect to the Kernel
    channel = grpc.insecure_channel('localhost:50051')
    stub = vryndara_pb2_grpc.KernelStub(channel)

    print("--- Sending Task to Coder Agent ---")
    
    # Create the message
    msg = vryndara_pb2.Signal(
        id=str(uuid.uuid4()), 
        source_agent_id="User-CLI", 
        target_agent_id="coder-alpha",
        type="TASK_REQUEST",
        payload="Write a python function to add two numbers",
        timestamp=int(time.time())
    )
    
    # Send it
    try:
        stub.Publish(msg)
        print("✅ Message Sent! Check your Agent terminal.")
    except grpc.RpcError as e:
        print(f"❌ Failed to connect to Kernel. Is it running? Error: {e.code()}")

if __name__ == "__main__":
    run()