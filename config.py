# ==========================================
# HIVEMQ CLOUD CONFIGURATION
# ==========================================

MQTT_BROKER = "0f1860f0ed1a409cba6412559af478c2.s1.eu.hivemq.cloud"
MQTT_PORT = 8883

# ==========================================
# LOGIN CREDENTIALS
# ==========================================

MQTT_USERNAME = "Shivaya_Mishra"
MQTT_PASSWORD = "Rakshita@34"

# ==========================================
# FLOOD EARLY WARNING MQTT TOPICS
# ==========================================

TOPIC_RAINFALL = "rainfall/data"         # Telemetry stream: rainfall & water level
TOPIC_PREDICTION = "flood/prediction"    # LSTM forecast results & risk state
TOPIC_FLOOD_ALERT = "flood/alert"        # Automated early warning triggers

# Legacy / Energy topics (preserved for compatibility)
ENERGY_TOPIC = "smart_energy/data"
ALERT_TOPIC = "smart_energy/alert"
TARIFF_PER_KWH = 8.0

# ==========================================
# WATER LEVEL THRESHOLDS (METERS)
# ==========================================
# Low / Normal water level : < 1.50 m
# Moderate / Watch (Advisory) : 1.50 m to 2.00 m
# High Risk (Warning) : 2.00 m to 2.50 m
# Critical Flood (Emergency) : > 2.50 m
LEVEL_SAFE_MAX = 1.50
LEVEL_WATCH_MAX = 2.00
LEVEL_WARNING_MAX = 2.50

# Sequence length for LSTM window (timesteps)
SEQUENCE_LENGTH = 5