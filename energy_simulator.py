import random
import time
from datetime import datetime


def generate_energy_data():
    voltage = round(random.uniform(220, 240), 2)
    current = round(random.uniform(2, 10), 2)

    power = round(voltage * current, 2)

    power_factor = round(random.uniform(0.80, 0.99), 2)

    energy = round(power / 1000, 3)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "voltage": voltage,
        "current": current,
        "power": power,
        "power_factor": power_factor,
        "energy": energy
    }


if __name__ == "__main__":
    while True:
        data = generate_energy_data()
        print(data)
        time.sleep(2)