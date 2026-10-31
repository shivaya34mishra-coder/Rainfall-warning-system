import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest


# =====================================
# CREATE TRAINING DATA
# =====================================

np.random.seed(42)

samples = 1000


# Normal voltage around 230V

voltage = np.random.normal(
    230,
    3,
    samples
)


# Normal current around 5A

current = np.random.normal(
    5,
    1,
    samples
)


# Normal power factor around 0.92

power_factor = np.random.normal(
    0.92,
    0.03,
    samples
)


# Calculate power

power = (
    voltage
    *
    current
    *
    power_factor
)


# =====================================
# CREATE DATAFRAME
# =====================================

data = pd.DataFrame({

    "voltage": voltage,

    "current": current,

    "power": power,

    "power_factor": power_factor

})


# =====================================
# SELECT FEATURES
# =====================================

features = [

    "voltage",

    "current",

    "power",

    "power_factor"

]


X = data[features]


# =====================================
# CREATE ML MODEL
# =====================================

model = IsolationForest(

    contamination=0.05,

    random_state=42

)


# =====================================
# TRAIN MODEL
# =====================================

model.fit(X)


# =====================================
# SAVE MODEL
# =====================================

joblib.dump(

    {

        "model": model,

        "features": features

    },

    "ml_model.joblib"

)


print()

print(
    "ML MODEL TRAINED SUCCESSFULLY"
)

print()

print(
    "Model file created:"
)

print(
    "ml_model.joblib"
)