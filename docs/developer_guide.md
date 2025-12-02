## 1. Create a clean Python 3.10 environment for conda 
conda create -n vryndara python=3.10 -y

# 2. Activate it
conda activate vryndara

# 3. Install PyTorch with CUDA 11.8 support (Best compatibility for LLMs)
# This command forces the GPU version explicitly.
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 4. Now install your project requirements
pip install -r requirements.txt

--------------------------------------------------------------------------------------

## Make sure you use the py launcher to pick 3.10 for venv install
py -3.10 -m venv venv

# Activate
.\venv\Scripts\activate

# Install PyTorch for CUDA 11.8 (The specific index-url is key for Windows)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install -r requirements.txt

----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------

# Run in terminal 
python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/vryndara.proto
python kernel/main.py

# Create __init__.py in every folder
New-Item -ItemType File -Force __init__.py
New-Item -ItemType File -Force kernel/__init__.py
New-Item -ItemType File -Force agents/__init__.py
New-Item -ItemType File -Force agents/coder/__init__.py
New-Item -ItemType File -Force protos/__init__.py
New-Item -ItemType File -Force sdk/__init__.py
New-Item -ItemType File -Force sdk/python/__init__.py
New-Item -ItemType File -Force sdk/python/vryndara/__init__.py

-----------------------------------------------------------------------------------------------

## Install Vryndara in "Editable Mode"
# This is the magic step. It links your folder to Python's internal library list.

pip install -e .
# Expected Output: You should see Successfully installed vryndara-0.1.0.