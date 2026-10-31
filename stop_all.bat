@echo off
title Stop Flood Warning System
color 0c
echo ======================================================================
echo       STOPPING FLOOD EARLY WARNING SYSTEM SERVICES
echo ======================================================================
echo.

echo Stopping Python services (Simulator, Forecaster, Streamlit)...
taskkill /F /FI "WINDOWTITLE eq 1. LSTM Flood Forecaster*" /T 2>nul
taskkill /F /FI "WINDOWTITLE eq 2. Rainfall Sensor Streamer*" /T 2>nul
taskkill /F /FI "WINDOWTITLE eq 4. Streamlit Dashboard*" /T 2>nul

echo Stopping Node-RED...
taskkill /F /FI "WINDOWTITLE eq 3. Node-RED IoT Server*" /T 2>nul

echo.
echo All services stopped cleanly.
echo.
pause
