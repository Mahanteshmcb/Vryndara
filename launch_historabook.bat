@echo off
title Historabook Server
color 0E
echo ===================================================
echo           LAUNCHING HISTORABOOK APP
echo ===================================================

:: --- CONFIGURATION (NO QUOTES) ---
set H_ROOT=C:\Users\Mahantesh\DevelopmentProjects\Historabook
set H_PY=C:\Users\Mahantesh\.conda\envs\historabook_env\python.exe
:: ---------------------------------

if exist "%H_ROOT%" (
    echo - Target: %H_ROOT%\backend
    echo - Python: %H_PY%
    
    :: Logic: Enter backend -> Set Offline Mode -> Run Uvicorn
    start "App: Historabook" powershell -NoExit -Command "cd '%H_ROOT%\backend'; $env:HF_HUB_OFFLINE='1'; & '%H_PY%' -m uvicorn app.main:app --reload --port 8001"
) else (
    echo ❌ ERROR: Folder not found at %H_ROOT%
    pause
)