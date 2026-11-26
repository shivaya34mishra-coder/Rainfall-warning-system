================================================================================
  PROJECT SUBMISSION: RAINFALL-BASED FLOOD EARLY WARNING SYSTEM (FEWS)
================================================================================

Student / Developer : Shivaya Mishra
Project Domain      : Internet of Things (IoT) & Deep Learning
Target Tech Stack   : HiveMQ Cloud MQTT, Python 3.13, PyTorch 2.15 (LSTM), Node-RED, Streamlit
GitHub Repository   : https://github.com/shivaya34mishra-coder/Rainfall-warning-system

--------------------------------------------------------------------------------
1. PROJECT DELIVERABLES INCLUDED IN THIS PACKAGE
--------------------------------------------------------------------------------
[A] Code Files:
    - flood_forecaster.py    : Real-time service running PyTorch LSTM inference and early warning dispatch
    - rainfall_simulator.py  : Sensor station telemetry streamer publishing to HiveMQ Cloud MQTT
    - lstm_model.py          : 2-Layer PyTorch LSTM neural network architecture & normalization pipeline
    - train_lstm.py          : Catchment runoff training script (achieving R² = 99.73%)
    - flood_dashboard.py     : Interactive Streamlit web command center with GIS map & hydrographs
    - config.py              : Cloud broker configuration, MQTT topics, and safety thresholds
    - flow.json              : Industrial Node-RED flow (gauges, hydrograph charts, toast alarms)
    - run_all.bat            : One-click Windows batch script to launch all services
    - stop_all.bat           : One-click script to terminate services cleanly

[B] Trained AI Model:
    - flood_lstm_model.pth   : Pre-trained PyTorch LSTM weights (RMSE: 0.0476m, MAE: 0.0217m)
    - scaler_params.json     : Mean and standard deviation scaling parameters

[C] Project Synopsis:
    - Project_Synopsis_FEWS.pdf : Full formal project synopsis in PDF format
    - synopsis.html             : Standalone formatted HTML synopsis report

[D] System Screenshots (in /screenshots):
    - 01_live_command_center.png   : Live telemetry command center, KPI tiles & hydrograph
    - 02_gis_flood_map.png         : Geographical GIS map with color-coded water level stations
    - 03_river_cross_section.png   : Hydraulic river channel elevation & inundation levee model
    - 04_system_architecture.png   : Complete system architecture & event-driven data pipeline

--------------------------------------------------------------------------------
2. HOW TO EXECUTE THE PROJECT
--------------------------------------------------------------------------------
Method 1 (One-Click):
    Double-click 'run_all.bat' to launch all microservices and open the dashboard.

Method 2 (Manual Terminal Execution):
    Terminal 1: python flood_forecaster.py
    Terminal 2: python rainfall_simulator.py
    Terminal 3: node-red (Access UI at http://localhost:1880/ui)
    Terminal 4: streamlit run flood_dashboard.py (Access UI at http://localhost:8501)

--------------------------------------------------------------------------------
3. ONLINE REPOSITORY LINK
--------------------------------------------------------------------------------
GitHub: https://github.com/shivaya34mishra-coder/Rainfall-warning-system
================================================================================
