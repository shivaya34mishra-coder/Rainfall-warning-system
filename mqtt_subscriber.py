import json
import ssl

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    ENERGY_TOPIC
)


# ==========================================
# WHEN CONNECTED
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    if reason_code == 0:

        print("SUCCESS: Connected to HiveMQ Cloud!")

        client.subscribe(ENERGY_TOPIC)

        print("Subscribed to:", ENERGY_TOPIC)

    else:

        print("Connection failed. Code:", reason_code)


# ==========================================
# WHEN MESSAGE ARRIVES
# ==========================================

def on_message(client, userdata, message):

    try:

        # Decode MQTT data
        payload = message.payload.decode()

        # Convert JSON to Python dictionary
        data = json.loads(payload)

        # Save latest data
        with open("latest_data.json", "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )

        print("\nNEW DATA RECEIVED")

        print(
            json.dumps(
                data,
                indent=4
            )
        )

    except Exception as error:

        print("ERROR:", error)


# ==========================================
# CREATE MQTT CLIENT
# ==========================================

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="smart_energy_subscriber"
)


# Username and Password
client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)


# TLS Security
client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)


# Callbacks
client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# CONNECT TO HIVEMQ
# ==========================================

print("Connecting to HiveMQ Cloud...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)


# ==========================================
# KEEP RUNNING
# ==========================================

print("Waiting for energy data...\n")

client.loop_forever()