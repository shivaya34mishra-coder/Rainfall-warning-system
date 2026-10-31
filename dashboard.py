import json
import time
import os

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import joblib

from config import TARIFF_PER_KWH


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Energy Management",
    layout="wide"
)
# ==========================================
# LOAD MACHINE LEARNING MODEL
# ==========================================

@st.cache_resource
def load_ml_model():

    return joblib.load(
        "ml_model.joblib"
    )


ml_data = load_ml_model()

ml_model = ml_data["model"]

ml_features = ml_data["features"]


# ==========================================
# INITIALIZE DATA HISTORY
# ==========================================

if "data_history" not in st.session_state:

    st.session_state.data_history = []


if "last_timestamp" not in st.session_state:

    st.session_state.last_timestamp = ""


# ==========================================
# READ LATEST DATA
# ==========================================

def read_latest_data():

    try:

        if os.path.exists(
            "latest_data.json"
        ):

            with open(
                "latest_data.json",
                "r"
            ) as file:

                data = json.load(
                    file
                )

            return data


        return {}


    except Exception as error:

        st.error(
            f"Data Reading Error: {error}"
        )

        return {}


# ==========================================
# READ DATA
# ==========================================

data = read_latest_data()


# ==========================================
# TITLE
# ==========================================

st.title(
    "⚡ Smart Industrial Energy Management System"
)


st.subheader(
    "Python + MQTT + HiveMQ Cloud"
)


# ==========================================
# DISPLAY DATA
# ==========================================

if data:
    # ======================================
    # MACHINE LEARNING PREDICTION
    # ======================================

    try:

        ml_input = pd.DataFrame(

            [{

                "voltage":
                data.get("voltage", 0),

                "current":
                data.get("current", 0),

                "power":
                data.get("power", 0),

                "power_factor":
                data.get("power_factor", 0)

            }]

        )


        prediction = ml_model.predict(

            ml_input[ml_features]

        )[0]


        anomaly_score = ml_model.decision_function(

            ml_input[ml_features]

        )[0]


        if prediction == -1:

            ml_status = (
                "ANOMALY DETECTED"
            )

        else:

            ml_status = (
                "NORMAL OPERATION"
            )


    except Exception as e:

        ml_status = (
            "ML ERROR"
        )

        anomaly_score = 0
    
        print(
            "ML Error:",
            e
        )
            # ======================================
    # MACHINE LEARNING ANALYSIS
    # ======================================

    st.subheader(
        "🤖 Machine Learning Analysis"
    )


    ml_col1, ml_col2 = st.columns(
        2
    )


    ml_col1.metric(

        "ML Status",

        ml_status

    )


    ml_col2.metric(

        "Anomaly Score",

        f"{anomaly_score:.4f}"

    )


    if ml_status == "ANOMALY DETECTED":

        st.error(
            "⚠️ Abnormal energy consumption detected!"
        )


    elif ml_status == "NORMAL OPERATION":

        st.success(
            "✅ Energy consumption is normal."
        )


    else:

        st.warning(
            "ML analysis unavailable."
        )

    # ======================================
    # ADD NEW DATA TO HISTORY
    # ======================================

    timestamp = data.get(
        "timestamp",
        ""
    )


    if (
        timestamp
        !=
        st.session_state.last_timestamp
    ):


        st.session_state.data_history.append(
            data.copy()
        )


        st.session_state.last_timestamp = (
            timestamp
        )


        # Keep last 100 readings

        if len(
            st.session_state.data_history
        ) > 100:

            st.session_state.data_history.pop(
                0
            )


    # ======================================
    # ENERGY CALCULATION
    # ======================================

    energy = float(
        data.get(
            "energy",
            0
        )
    )


    cost = (
        energy
        *
        TARIFF_PER_KWH
    )


    # ======================================
    # LIVE STATUS
    # ======================================

    st.success(
        "🟢 LIVE DATA RECEIVED FROM HIVEMQ CLOUD"
    )


    # ======================================
    # MAIN METRICS
    # ======================================

    st.subheader(
        "⚡ Live Electrical Parameters"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    col1.metric(

        "Voltage",

        f"{data.get('voltage', 0)} V"

    )


    col2.metric(

        "Current",

        f"{data.get('current', 0)} A"

    )


    col3.metric(

        "Power",

        f"{data.get('power', 0)} W"

    )


    col4.metric(

        "Energy",

        f"{energy:.3f} kWh"

    )


    # ======================================
    # SECONDARY METRICS
    # ======================================

    col5, col6, col7 = st.columns(
        3
    )


    col5.metric(

        "Power Factor",

        data.get(
            "power_factor",
            0
        )

    )


    col6.metric(

        "Energy Cost",

        f"₹ {cost:.2f}"

    )


    col7.metric(

        "Last Update",

        timestamp

    )


    # ======================================
    # POWER CONSUMPTION GRAPH
    # ======================================

    if len(
        st.session_state.data_history
    ) > 1:


        df = pd.DataFrame(

            st.session_state.data_history

        )


        st.subheader(
            "📊 Power Consumption Trend"
        )


        fig = go.Figure()


        fig.add_trace(

            go.Scatter(

                x=df["timestamp"],

                y=df["power"],

                mode="lines+markers",

                name="Power"

            )

        )


        fig.update_layout(

            xaxis_title="Time",

            yaxis_title="Power (W)",

            height=400

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ======================================
    # DATA TABLE
    # ======================================

    if len(
        st.session_state.data_history
    ) > 0:


        st.subheader(
            "📋 Recent Energy Readings"
        )


        history_df = pd.DataFrame(

            st.session_state.data_history

        )


        st.dataframe(

            history_df.tail(10),

            use_container_width=True

        )


else:


    st.warning(

        "⚠️ Waiting for energy data..."

    )


    st.info(

        """
        Check that:

        1. energy_simulator.py is running
        2. mqtt_subscriber.py is running
        3. latest_data.json exists
        """

    )


# ==========================================
# AUTO REFRESH
# ==========================================

time.sleep(2)

st.rerun()