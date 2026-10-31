import json
import os
import torch
import torch.nn as nn


class FloodLSTM(nn.Module):
    """
    LSTM Neural Network for Rainfall-Runoff & Water Level Forecasting.
    Takes a time-series sequence of [rainfall, water_level] and predicts
    the water level for the subsequent time step.
    """
    def __init__(self, input_dim=2, hidden_dim=64, num_layers=2, output_dim=1, dropout=0.2):
        super(FloodLSTM, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc1 = nn.Linear(hidden_dim, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, output_dim)

    def forward(self, x):
        # x shape: [batch_size, seq_len, input_dim]
        out, _ = self.lstm(x)
        # Select the output from the final sequence step
        last_step = out[:, -1, :]
        feat = self.relu(self.fc1(last_step))
        prediction = self.fc2(feat)
        return prediction


def load_scaler_params(params_path="scaler_params.json"):
    """Loads mean and standard deviation for input normalization."""
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"Scaler parameters file not found at {params_path}")
    with open(params_path, "r") as f:
        return json.load(f)


def normalize_sequence(sequence, scaler_params):
    """
    Normalizes a sequence of shape (seq_len, 2) where cols are [rainfall, water_level].
    sequence: list of [rainfall, water_level]
    """
    rain_mean = scaler_params["rain_mean"]
    rain_std = scaler_params["rain_std"] if scaler_params["rain_std"] > 1e-6 else 1.0
    water_mean = scaler_params["water_mean"]
    water_std = scaler_params["water_std"] if scaler_params["water_std"] > 1e-6 else 1.0

    norm_seq = []
    for r, w in sequence:
        norm_r = (r - rain_mean) / rain_std
        norm_w = (w - water_mean) / water_std
        norm_seq.append([norm_r, norm_w])
    return norm_seq


def denormalize_water_level(norm_val, scaler_params):
    """Converts normalized water level back to physical meters."""
    water_mean = scaler_params["water_mean"]
    water_std = scaler_params["water_std"] if scaler_params["water_std"] > 1e-6 else 1.0
    return (norm_val * water_std) + water_mean
