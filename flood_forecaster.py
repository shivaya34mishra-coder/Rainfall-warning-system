import collections
import datetime
import json
import os
import ssl
import sys
import time
import torch
import paho.mqtt.client as mqtt

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


class FloodForecasterService:
    def __init__(self, model_path="flood_lstm_model.pth", scaler_path="scaler_params.json"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[Model] Loading LSTM model on device: {self.device}", flush=True)
        
        # Load scaler
        self.scaler = load_scaler_params(scaler_path)
        
        # Load model architecture & weights
        self.model = FloodLSTM(input_dim=2, hidden_dim=64, num_layers=2, output_dim=1, dropout=0.2).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        print("[Model] LSTM neural network weights successfully loaded.", flush=True)

        # Sliding window buffer: stores list of [rainfall, water_level]
        self.buffer = collections.deque(maxlen=SEQUENCE_LENGTH)

        # MQTT Client
        self.mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="flood_lstm_forecaster"
        )
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.mqtt_client.tls_set(
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print(f"[MQTT] Connected to HiveMQ Cloud. Subscribing to: {TOPIC_RAINFALL}", flush=True)
            client.subscribe(TOPIC_RAINFALL, qos=1)
        else:
            print(f"[MQTT] Connection failed with code: {reason_code}", flush=True)

    def evaluate_risk(self, predicted_level, current_level):
        diff = predicted_level - current_level
        if predicted_level < LEVEL_SAFE_MAX:
            risk = "SAFE"
            msg = "Water level is within safe bounds. No flood threat."
            action = "Routine hydrological monitoring."
        elif predicted_level < LEVEL_WATCH_MAX:
            risk = "WATCH"
            msg = "Moderate rise detected (ADVISORY). Water levels increasing."
            action = "Alert drainage teams and monitor low-lying retention basins."
        elif predicted_level < LEVEL_WARNING_MAX:
            risk = "WARNING"
            msg = "HIGH FLOOD RISK — Water approaching riverbank crest!"
            action = "Open flood retention gates and prepare sandbag defenses."
        else:
            risk = "CRITICAL"
            msg = "CRITICAL FLOOD WARNING — Inundation imminent! Take immediate action."
            action = "Sound community sirens and execute emergency evacuation protocol."

        return risk, msg, action, diff

    def run_inference(self):
        # Convert buffer to numpy/list sequence
        seq = list(self.buffer)
        norm_seq = normalize_sequence(seq, self.scaler)
        
        # Prepare tensor [1, seq_len, 2]
        tensor_input = torch.tensor([norm_seq], dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            norm_pred = self.model(tensor_input).cpu().item()
            pred_level = denormalize_water_level(norm_pred, self.scaler)

        return max(0.5, float(pred_level))

    def on_message(self, client, userdata, message):
        try:
            payload_str = message.payload.decode("utf-8")
            data = json.loads(payload_str)

            rain = float(data.get("rainfall", 0.0))
            water = float(data.get("water_level", 0.0))
            ts = data.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())

            # Append to sliding history buffer
            self.buffer.append([rain, water])

            if len(self.buffer) < SEQUENCE_LENGTH:
                print(f"[Buffer] Accumulating historical context ({len(self.buffer)}/{SEQUENCE_LENGTH})...", flush=True)
                return

            # Run LSTM forecasting
            predicted_water = self.run_inference()
            risk_level, warning_msg, action, diff = self.evaluate_risk(predicted_water, water)

            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            # Construct automated result payload
            prediction_payload = {
                "timestamp": now_iso,
                "sensor_timestamp": ts,
                "rainfall": round(rain, 2),
                "current_water_level": round(water, 3),
                "predicted_water_level": round(predicted_water, 3),
                "rate_of_rise": round(diff, 3),
                "risk_level": risk_level,
                "warning_message": warning_msg,
                "recommended_action": action,
                "alert_triggered": risk_level in ["WARNING", "CRITICAL"]
            }

            # 1. Publish forecast result to flood/prediction
            client.publish(TOPIC_PREDICTION, json.dumps(prediction_payload), qos=1)

            # 2. If Warning or Critical, trigger automated alert
            if prediction_payload["alert_triggered"]:
                alert_payload = {
                    "alert_id": f"ALT-{int(time.time())}",
                    "timestamp": now_iso,
                    "risk_level": risk_level,
                    "severity": "CRITICAL" if risk_level == "CRITICAL" else "HIGH",
                    "current_level": round(water, 3),
                    "forecast_level": round(predicted_water, 3),
                    "message": warning_msg,
                    "action_required": action
                }
                client.publish(TOPIC_FLOOD_ALERT, json.dumps(alert_payload), qos=1)

            # Format console log
            trend_symbol = "+" if diff >= 0 else ""
            print(f"[{now_str}] Rain: {rain:>4.1f}mm | Curr: {water:>4.2f}m -> Forecast: {predicted_water:>4.2f}m ({trend_symbol}{diff:>.2f}m) | Risk: [{risk_level}]", flush=True)
            if prediction_payload["alert_triggered"]:
                print(f"   >>> AUTOMATED EARLY WARNING TRIGGERED: {warning_msg}", flush=True)

        except Exception as e:
            print(f"[Error processing message] {e}", flush=True)

    def start(self):
        print("=" * 65, flush=True)
        print("  AUTOMATED LSTM FLOOD FORECASTING & EARLY WARNING ENGINE", flush=True)
        print("=" * 65, flush=True)
        print(f"Broker       : {MQTT_BROKER}:{MQTT_PORT}", flush=True)
        print(f"Input Topic  : {TOPIC_RAINFALL}", flush=True)
        print(f"Output Topic : {TOPIC_PREDICTION}", flush=True)
        print(f"Alert Topic  : {TOPIC_FLOOD_ALERT}", flush=True)
        print("=" * 65, flush=True)

        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        print("[Forecaster] Listening for real-time sensor streams...\n", flush=True)
        self.mqtt_client.loop_forever()


if __name__ == "__main__":
    try:
        service = FloodForecasterService()
        service.start()
    except KeyboardInterrupt:
        print("\n[Terminated] Flood forecaster stopped.", flush=True)
    except Exception as e:
        print(f"[Fatal Error] {e}", flush=True)
