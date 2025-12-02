#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Generate gRPC code from proto
# We output it into the root so both Kernel and SDK can see it easily
python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/vryndara.proto

echo "✅ Setup complete. Proto files generated."./scripts/setup.sh
python kernel/main.py