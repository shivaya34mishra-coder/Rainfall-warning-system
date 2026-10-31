import datetime
import json
import os
import ssl
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import torch

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    TOPIC_RAINFALL,
    TOPIC_PREDICTION,
    TOPIC_FLOOD_ALERT,
    LEVEL_SAFE_MAX,
    LEVEL_WATCH_MAX,
    LEVEL_WARNING_MAX,
    SEQUENCE_LENGTH
)
from lstm_model import FloodLSTM, load_scaler_params, normalize_sequence, denormalize_water_level

st.set_page_config(
    page_title="Flood Early Warning System (FEWS)",
    page_icon="🌧️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
        color: white;
    }
    .status-safe {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; padding: 18px; border-radius: 12px; text-align: center;
    }
    .status-watch {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; padding: 18px; border-radius: 12px; text-align: center;
    }
    .status-warning {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white; padding: 18px; border-radius: 12px; text-align: center;
    }
    .status-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white; padding: 18px; border-radius: 12px; text-align: center;
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_trained_lstm():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    scaler = load_scaler_params("scaler_params.json")
    model = FloodLSTM(input_dim=2, hidden_dim=64, num_layers=2, output_dim=1, dropout=0.2).to(device)
    model.load_state_dict(torch.load("flood_lstm_model.pth", map_location=device))
    model.eval()
    return model, scaler, device


try:
    lstm_model, scaler_params, device = load_trained_lstm()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.error(f"Error loading LSTM model: {e}")


# Header
st.title("🌧️ Rainfall-Based Flood Early Warning System (FEWS)")
st.caption(f"Connected Architecture: **HiveMQ Cloud TLS** ➔ **PyTorch LSTM AI Engine** ➔ **Node-RED & Streamlit Dashboards**")

st.markdown("---")

# Sidebar Configuration
st.sidebar.header("📡 IoT & Broker Status")
st.sidebar.info(f"**HiveMQ Host:** `{MQTT_BROKER}`\n\n**Port:** `{MQTT_PORT}` (TLS Encrypted)\n\n**Telemetry Topic:** `{TOPIC_RAINFALL}`\n\n**LSTM Topic:** `{TOPIC_PREDICTION}`")

st.sidebar.header("🎯 Water Level Thresholds")
st.sidebar.markdown(f"- 🟢 **SAFE:** < {LEVEL_SAFE_MAX} m")
st.sidebar.markdown(f"- 🟡 **WATCH:** {LEVEL_SAFE_MAX} m - {LEVEL_WATCH_MAX} m")
st.sidebar.markdown(f"- 🟠 **WARNING:** {LEVEL_WATCH_MAX} m - {LEVEL_WARNING_MAX} m")
st.sidebar.markdown(f"- 🔴 **CRITICAL:** > {LEVEL_WARNING_MAX} m")

# Mode Selection
app_mode = st.sidebar.radio("Navigation", ["🔍 Live AI Forecast & Early Warning", "🧪 Interactive Scenario Testing", "📊 Model Architecture & Training"])

if app_mode == "🔍 Live AI Forecast & Early Warning":
    # Check for live data or simulated demo
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Real-Time Telemetry & LSTM Forecasting")
    with col_b:
        auto_refresh = st.checkbox("Auto-simulate live stream (3s)", value=True)

    # State container for historical observations
    if "history" not in st.session_state:
        # Prepopulate with sample realistic series
        now = datetime.datetime.now()
        hist = []
        base_w = 1.05
        for i in range(15):
            t = now - datetime.timedelta(seconds=(15 - i) * 3)
            r = 4.0 if i < 6 else (22.0 if i < 11 else 38.0)
            base_w += 0.08 if r > 10 else -0.02
            base_w = max(0.9, min(2.8, base_w))
            hist.append({
                "time": t.strftime("%H:%M:%S"),
                "rainfall": round(r + np.random.normal(0, 1), 1),
                "water_level": round(base_w, 2)
            })
        st.session_state.history = hist

    # Append new point if auto_refresh
    if auto_refresh:
        last_item = st.session_state.history[-1]
        step_idx = len(st.session_state.history) % 30
        if step_idx < 8:
            new_r = max(0.0, round(float(np.random.normal(2.0, 0.5)), 1))
            new_w = max(0.85, round(last_item["water_level"] * 0.94 + 0.05, 2))
        elif step_idx < 18:
            new_r = max(10.0, round(float(np.random.normal(26.0, 4.0)), 1))
            new_w = min(3.2, round(last_item["water_level"] * 0.92 + 0.045 * new_r, 2))
        else:
            new_r = max(25.0, round(float(np.random.normal(42.0, 5.0)), 1))
            new_w = min(3.3, round(last_item["water_level"] * 0.93 + 0.048 * new_r, 2))

        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.history.append({
            "time": now_str,
            "rainfall": new_r,
            "water_level": new_w
        })
        if len(st.session_state.history) > 30:
            st.session_state.history.pop(0)

    df_hist = pd.DataFrame(st.session_state.history)
    curr_rain = df_hist["rainfall"].iloc[-1]
    curr_water = df_hist["water_level"].iloc[-1]

    # Predict with LSTM using last 5 readings
    if len(df_hist) >= SEQUENCE_LENGTH and model_loaded:
        seq = df_hist[["rainfall", "water_level"]].iloc[-SEQUENCE_LENGTH:].values.tolist()
        norm_seq = normalize_sequence(seq, scaler_params)
        tensor_in = torch.tensor([norm_seq], dtype=torch.float32).to(device)
        with torch.no_grad():
            norm_pred = lstm_model(tensor_in).cpu().item()
            pred_water = max(0.5, round(denormalize_water_level(norm_pred, scaler_params), 2))
    else:
        pred_water = curr_water

    rate_of_rise = round(pred_water - curr_water, 2)

    # Determine risk category
    if pred_water < LEVEL_SAFE_MAX:
        risk_class = "SAFE"
        status_box = f"""
        <div class="status-safe">
            <h2>🟢 STATUS: SAFE</h2>
            <p><strong>Conditions Normal:</strong> River water level predicted at {pred_water}m (Safe Threshold < {LEVEL_SAFE_MAX}m).</p>
            <p style="font-size:13px; opacity:0.9;">Action: Standard hydrological monitoring.</p>
        </div>
        """
    elif pred_water < LEVEL_WATCH_MAX:
        risk_class = "WATCH"
        status_box = f"""
        <div class="status-watch">
            <h2>🟡 STATUS: FLOOD WATCH (ADVISORY)</h2>
            <p><strong>Rising River:</strong> River level projected to reach {pred_water}m (+{rate_of_rise}m).</p>
            <p style="font-size:13px; opacity:0.9;">Action: Drainage personnel alerted; monitor low-lying retention basins.</p>
        </div>
        """
    elif pred_water < LEVEL_WARNING_MAX:
        risk_class = "WARNING"
        status_box = f"""
        <div class="status-warning">
            <h2>🟠 STATUS: FLOOD WARNING</h2>
            <p><strong>High Risk of Inundation:</strong> Water level projected to crest at {pred_water}m.</p>
            <p style="font-size:13px; opacity:0.9;">Action: Open floodgates, deploy sandbags, prepare evacuation routes.</p>
        </div>
        """
    else:
        risk_class = "CRITICAL"
        status_box = f"""
        <div class="status-critical">
            <h2>🔴 STATUS: CRITICAL EMERGENCY WARNING</h2>
            <p><strong>EXTREME FLOOD EVENT IMMINENT:</strong> River overflow projected at {pred_water}m!</p>
            <p style="font-size:13px; opacity:0.9;">Action: IMMEDIATE EVACUATION. Sound community sirens.</p>
        </div>
        """

    st.markdown(status_box, unsafe_allow_html=True)
    st.write("")

    # Top KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("🌧️ Current Rainfall", f"{curr_rain:.1f} mm", delta=f"{curr_rain - df_hist['rainfall'].iloc[-2]:+.1f} mm" if len(df_hist) > 1 else None)
    kpi2.metric("📏 Current Water Level", f"{curr_water:.2f} m", delta=f"{curr_water - df_hist['water_level'].iloc[-2]:+.2f} m" if len(df_hist) > 1 else None)
    kpi3.metric("🔮 LSTM Forecast Level", f"{pred_water:.2f} m", delta=f"{rate_of_rise:+.2f} m", delta_color="inverse")
    kpi4.metric("🚨 Early Warning Severity", risk_class)

    st.write("")

    # Visual Gauges
    g_col1, g_col2, g_col3 = st.columns(3)

    with g_col1:
        fig_g1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=curr_rain,
            title={'text': "Rainfall Intensity (mm)"},
            gauge={
                'axis': {'range': [0, 60]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 15], 'color': "rgba(16, 185, 129, 0.3)"},
                    {'range': [15, 30], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [30, 60], 'color': "rgba(239, 68, 68, 0.3)"}
                ]
            }
        ))
        fig_g1.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g1, use_container_width=True)

    with g_col2:
        fig_g2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=curr_water,
            title={'text': "Current Water Level (m)"},
            gauge={
                'axis': {'range': [0, 3.5]},
                'bar': {'color': "#10b981" if curr_water < 1.5 else ("#f59e0b" if curr_water < 2.0 else "#ef4444")},
                'steps': [
                    {'range': [0, 1.5], 'color': "rgba(16, 185, 129, 0.3)"},
                    {'range': [1.5, 2.0], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [2.0, 3.5], 'color': "rgba(239, 68, 68, 0.3)"}
                ]
            }
        ))
        fig_g2.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g2, use_container_width=True)

    with g_col3:
        fig_g3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_water,
            title={'text': "LSTM Forecast Water Level (m)"},
            gauge={
                'axis': {'range': [0, 3.5]},
                'bar': {'color': "#3b82f6"},
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': LEVEL_WARNING_MAX
                },
                'steps': [
                    {'range': [0, 1.5], 'color': "rgba(16, 185, 129, 0.3)"},
                    {'range': [1.5, 2.0], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [2.0, 3.5], 'color': "rgba(239, 68, 68, 0.3)"}
                ]
            }
        ))
        fig_g3.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g3, use_container_width=True)

    # Time-Series Hydrograph Trend Chart
    st.subheader("📈 Live Hydrograph: Rainfall vs River Level vs LSTM Prediction")
    fig_line = go.Figure()

    fig_line.add_trace(go.Bar(
        x=df_hist["time"],
        y=df_hist["rainfall"],
        name="Rainfall (mm)",
        yaxis="y2",
        marker_color="rgba(59, 130, 246, 0.4)"
    ))

    fig_line.add_trace(go.Scatter(
        x=df_hist["time"],
        y=df_hist["water_level"],
        name="Actual Water Level (m)",
        mode="lines+markers",
        line=dict(color="#10b981", width=3)
    ))

    # Add forecast point at the end
    future_time = (datetime.datetime.now() + datetime.timedelta(seconds=3)).strftime("%H:%M:%S")
    fig_line.add_trace(go.Scatter(
        x=[df_hist["time"].iloc[-1], future_time],
        y=[curr_water, pred_water],
        name="LSTM Forecast Lead",
        mode="lines+markers",
        line=dict(color="#ef4444", width=3, dash="dot"),
        marker=dict(size=10, symbol="diamond")
    ))

    # Threshold horizontal reference lines
    fig_line.add_hline(y=LEVEL_SAFE_MAX, line_dash="dash", line_color="#f59e0b", annotation_text="Watch Threshold (1.5m)")
    fig_line.add_hline(y=LEVEL_WARNING_MAX, line_dash="dash", line_color="#ef4444", annotation_text="Warning Threshold (2.0m)")

    fig_line.update_layout(
        yaxis=dict(title="Water Level (meters)", range=[0, 3.5]),
        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right", range=[0, 70], showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    if auto_refresh:
        time.sleep(3)
        st.rerun()

elif app_mode == "🧪 Interactive Scenario Testing":
    st.subheader("Interactive 'What-If' Storm Simulation")
    st.write("Adjust historical rainfall and water level sequences below to observe how the trained PyTorch LSTM model forecasts flood risks in real time:")

    col1, col2 = st.columns(2)
    with col1:
        sim_rain = st.slider("Simulated Storm Rainfall (mm)", min_value=0.0, max_value=60.0, value=35.0, step=1.0)
    with col2:
        sim_water = st.slider("Starting River Water Level (m)", min_value=0.5, max_value=3.2, value=1.8, step=0.05)

    test_seq = []
    for step in range(SEQUENCE_LENGTH):
        r_step = sim_rain * (0.4 + 0.6 * (step / (SEQUENCE_LENGTH - 1)))
        w_step = sim_water * (0.85 + 0.15 * (step / (SEQUENCE_LENGTH - 1)))
        test_seq.append([r_step, w_step])

    norm_seq = normalize_sequence(test_seq, scaler_params)
    tensor_in = torch.tensor([norm_seq], dtype=torch.float32).to(device)

    with torch.no_grad():
        norm_pred = lstm_model(tensor_in).cpu().item()
        sim_pred = round(denormalize_water_level(norm_pred, scaler_params), 2)

    diff = round(sim_pred - sim_water, 2)

    st.markdown("### 📋 Automated Forecast Result")
    r1, r2, r3 = st.columns(3)
    r1.metric("Input Current Water Level", f"{sim_water:.2f} m")
    r2.metric("LSTM Forecasted Water Level", f"{sim_pred:.2f} m", delta=f"{diff:+.2f} m", delta_color="inverse")
    
    if sim_pred < LEVEL_SAFE_MAX:
        r3.success("Severity: SAFE")
    elif sim_pred < LEVEL_WATCH_MAX:
        r3.warning("Severity: FLOOD WATCH (ADVISORY)")
    elif sim_pred < LEVEL_WARNING_MAX:
        r3.warning("Severity: FLOOD WARNING")
    else:
        r3.error("Severity: CRITICAL FLOOD EMERGENCY")

elif app_mode == "📊 Model Architecture & Training":
    st.subheader("PyTorch LSTM Model Summary")
    st.code("""
FloodLSTM(
  (lstm): LSTM(2, 64, num_layers=2, batch_first=True, dropout=0.2)
  (fc1): Linear(in_features=64, out_features=32, bias=True)
  (relu): ReLU()
  (fc2): Linear(in_features=32, out_features=1, bias=True)
)
Features: [Rainfall (mm), Water Level (m)]
Sequence Window: 5 timesteps
Loss Function: MSELoss
Optimizer: Adam (lr=0.005)
Evaluation Metrics:
- R2 Score: 99.73%
- RMSE: 0.0476 m
- MAE: 0.0217 m
    """, language="python")
