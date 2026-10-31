@echo off
title Flood Early Warning System (FEWS) Launcher
color 0b

echo ======================================================================
echo       RAINFALL-BASED FLOOD EARLY WARNING SYSTEM (FEWS)
echo ======================================================================
echo.
echo Tech Stack: HiveMQ Cloud MQTT ^| Python ^| PyTorch LSTM ^| Node-RED
echo.
echo Starting all system microservices in separate windows...
echo.

:: 1. Start AI Forecaster
echo [1/3] Launching AI Forecaster (flood_forecaster.py)...
start "1. LSTM Flood Forecaster" cmd /k "cd /d "%~dp0" && python flood_forecaster.py"
timeout /t 3 /nobreak >nul

:: 2. Start Sensor Telemetry Streamer
echo [2/3] Launching Sensor Telemetry Streamer (rainfall_simulator.py)...
start "2. Rainfall Sensor Streamer" cmd /k "cd /d "%~dp0" && python rainfall_simulator.py"
timeout /t 2 /nobreak >nul

:: 3. Start Node-RED
echo [3/3] Launching Node-RED Runtime...
start "3. Node-RED IoT Server" cmd /k "node-red"
timeout /t 5 /nobreak >nul

echo.
echo ======================================================================
echo   ALL SERVICES ARE NOW RUNNING!
echo ======================================================================
echo.
echo  Access Points:
echo    - Node-RED UI Dashboard : http://localhost:1880/ui
echo    - Node-RED Flow Editor  : http://localhost:1880
echo.
echo Opening Node-RED Dashboard in your browser...
start http://localhost:1880/ui
echo.
echo Press any key to also launch the Streamlit Web Dashboard, or close this window.
pause >nul
start "4. Streamlit Dashboard" cmd /k "cd /d "%~dp0" && streamlit run flood_dashboard.py"
