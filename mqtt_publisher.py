import json
import ssl
import time

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    ENERGY_TOPIC
)

from energy_simulator import generate_energy_data


# MQTT connection callback
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("SUCCESS: Connected to HiveMQ Cloud!")
    else:
        print(f"FAILED: Connection failed. Code: {reason_code}")


# Create MQTT client
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="smart_energy_system"
)

# Username and password
client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

# Enable TLS security
client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

# Set callback
client.on_connect = on_connect


try:
    print("Connecting to HiveMQ Cloud...")

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    client.loop_start()

    time.sleep(2)

    print("Starting Smart Energy Data Publisher...")
    print("Press Ctrl + C to stop.\n")

    while True:

        # Generate simulated energy data
        energy_data = generate_energy_data()

        # Convert data to JSON
        message = json.dumps(energy_data)

        # Publish to HiveMQ
        result = client.publish(
            ENERGY_TOPIC,
            message
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Published:", message)
        else:
            print("Publish failed!")

        time.sleep(2)


except KeyboardInterrupt:
    print("\nStopping Smart Energy Publisher...")


except Exception as e:
    print("ERROR:", e)


finally:
    try:
        client.loop_stop()
        client.disconnect()
    except:
        pass