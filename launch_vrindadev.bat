@echo off
title VrindaDev Studio
color 0D
echo ===================================================
echo            LAUNCHING VRINDADEV STUDIO
echo ===================================================

:: --- CONFIGURATION (NO QUOTES) ---
set V_ROOT=C:\Users\Mahantesh\DevelopmentProjects\VrindaDev
:: ---------------------------------

if exist "%V_ROOT%" (
    echo - Target: %V_ROOT%
    
    :: Logic: Enter folder -> npm start
    start "App: VrindaDev" powershell -NoExit -Command "cd '%V_ROOT%'; npm start"
) else (
    echo ❌ ERROR: Folder not found at %V_ROOT%
    pause
)