import datetime
import json
import random
import ssl
import sys
import time
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    TOPIC_RAINFALL
)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[MQTT] Successfully connected to HiveMQ Cloud Broker!")
    else:
        print(f"[MQTT] Connection failed with code: {reason_code}")


def create_mqtt_client():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="rainfall_sensor_station"
    )
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )
    client.on_connect = on_connect
    return client


class HydrologySimulator:
    """
    Simulates dynamic rainfall intensity and river catchment response.
    Cycles through: Normal -> Storm Surge -> Torrential Flood -> Recession.
    """
    def __init__(self):
        self.base_level = 0.90
        self.water_level = 0.95
        self.recent_rain = 1.0
        self.phase = "NORMAL"
        self.step_count = 0

    def next_step(self):
        self.step_count += 1
        
        # Weather cycle progression (every 12 steps changes phase)
        cycle_idx = (self.step_count // 12) % 4
        if cycle_idx == 0:
            self.phase = "NORMAL (Dry/Clear)"
            rainfall = max(0.0, random.gauss(1.5, 0.8))
            drain_target = self.base_level
        elif cycle_idx == 1:
            self.phase = "LIGHT/MODERATE RAIN"
            rainfall = max(5.0, random.gauss(14.0, 3.0))
            drain_target = 1.45
        elif cycle_idx == 2:
            self.phase = "HEAVY STORM (Flood Alert)"
            rainfall = max(22.0, random.gauss(38.0, 6.0))
            drain_target = 2.65
        else:
            self.phase = "RECEDING (Rain Cleared)"
            rainfall = max(0.0, random.gauss(2.0, 1.0))
            drain_target = 1.10

        # Physical catchment runoff lag: water level reacts to rain with inertia
        inflow = 0.045 * (0.6 * rainfall + 0.4 * self.recent_rain)
        recession = 0.88 * (self.water_level - drain_target)
        self.water_level = max(0.5, drain_target + recession + inflow + random.gauss(0, 0.02))
        self.water_level = min(3.40, self.water_level)
        self.recent_rain = rainfall

        return round(rainfall, 2), round(self.water_level, 3), self.phase


def main():
    print("=" * 65)
    print("  RAINFALL & WATER LEVEL TELEMETRY STREAMER (HIVEMQ CLOUD)")
    print("=" * 65)
    print(f"Target Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Target Topic : {TOPIC_RAINFALL}")
    print("=" * 65)

    client = create_mqtt_client()
    
    try:
        print("[Connecting] Establishing TLS session with HiveMQ Cloud...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        time.sleep(2)

        simulator = HydrologySimulator()
        interval_seconds = 3

        print(f"\n[Running] Streaming sensor readings every {interval_seconds}s...")
        print("Press Ctrl+C to terminate.\n")
        print(f"{'Time':<10} | {'Phase':<24} | {'Rainfall':<12} | {'Water Level':<12}")
        print("-" * 65)

        while True:
            rainfall, water_level, phase = simulator.next_step()
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            payload = {
                "timestamp": now_iso,
                "rainfall": rainfall,
                "water_level": water_level,
                "weather_condition": phase
            }

            msg_json = json.dumps(payload)
            pub_result = client.publish(TOPIC_RAINFALL, msg_json, qos=1)

            if pub_result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"{now_str:<10} | {phase:<24} | {rainfall:>5.1f} mm     | {water_level:>5.2f} m")
            else:
                print(f"[Warning] Publish failed with code {pub_result.rc}")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n[Stopped] Sensor streamer paused by user.")
    except Exception as e:
        print(f"\n[Error] {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[MQTT] Disconnected from HiveMQ Cloud.")


if __name__ == "__main__":
    main()
