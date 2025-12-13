@echo off
title Vryndara Core
color 0B
echo ===================================================
echo        LAUNCHING VRYNDARA OPERATING SYSTEM
echo ===================================================

:: --- CONFIGURATION (NO QUOTES) ---
set VPY=C:\Users\Mahantesh\.conda\envs\vryndara\python.exe
:: ---------------------------------

echo [1/4] Kernel...
start "Vryndara Kernel" powershell -NoExit -Command "$env:PYTHONPATH='.'; & '%VPY%' kernel/main.py"
timeout /t 2 >nul

echo [2/4] Gateway...
start "Vryndara Gateway" powershell -NoExit -Command "$env:PYTHONPATH='.'; & '%VPY%' -m uvicorn gateway.main:socket_app --host 0.0.0.0 --port 8081"
timeout /t 2 >nul

echo [3/4] Agents...
start "Agent: Media" powershell -NoExit -Command "$env:PYTHONPATH='.'; & '%VPY%' agents/media/main.py"
timeout /t 1 >nul
start "Agent: Coder" powershell -NoExit -Command "$env:PYTHONPATH='.'; & '%VPY%' agents/coder/main.py"
timeout /t 1 >nul
:: start "Agent: Researcher" powershell -NoExit -Command "$env:PYTHONPATH='.'; & '%VPY%' agents/researcher/main.py"

echo [4/4] UI...
cd ui
start "Dashboard" powershell -NoExit -Command "npm run dev"

echo ✅ Core System Online.