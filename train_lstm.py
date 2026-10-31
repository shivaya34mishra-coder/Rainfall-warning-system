import json
import math
import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from lstm_model import FloodLSTM
from config import SEQUENCE_LENGTH


def generate_hydrological_data(num_steps=4000, random_seed=42):
    """
    Generates realistic rainfall and river water level time-series data
    based on hydrological runoff dynamics with retention delay and river discharge recession.
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

    base_level = 0.85     # Base normal river level in meters
    max_storage = 3.5     # Maximum river bank capacity
    recession_rate = 0.92 # Water drainage coefficient per step
    runoff_coeff = 0.048  # Catchment runoff sensitivity to rainfall
    
    rainfall_series = np.zeros(num_steps)
    water_level_series = np.zeros(num_steps)
    
    # State machine for weather storms
    state = "dry"  # "dry", "light", "heavy_storm"
    state_steps = 0
    current_water = base_level

    for t in range(num_steps):
        # State transitions
        if state_steps <= 0:
            p = random.random()
            if p < 0.55:
                state = "dry"
                state_steps = random.randint(15, 35)
            elif p < 0.85:
                state = "light"
                state_steps = random.randint(10, 25)
            else:
                state = "heavy_storm"
                state_steps = random.randint(8, 20)

        # Generate rainfall intensity (mm) based on current weather state
        if state == "dry":
            rain = max(0.0, np.random.normal(0.5, 0.4))
        elif state == "light":
            rain = max(1.0, np.random.normal(8.0, 3.0))
        else: # heavy storm / cloudburst
            rain = max(18.0, np.random.normal(36.0, 8.5))
        
        rainfall_series[t] = round(rain, 2)
        state_steps -= 1

        # Hydrological runoff calculation with 1-step and 2-step lag
        recent_rain = rain
        prev_rain = rainfall_series[t - 1] if t >= 1 else 0.0
        prev2_rain = rainfall_series[t - 2] if t >= 2 else 0.0
        
        effective_inflow = (0.35 * recent_rain + 0.45 * prev_rain + 0.20 * prev2_rain) * runoff_coeff

        # River level recession + inflow surge + stochastic noise
        current_water = base_level + (current_water - base_level) * recession_rate + effective_inflow
        current_water += np.random.normal(0.0, 0.015)
        current_water = min(max_storage, max(0.5, current_water))
        
        water_level_series[t] = round(current_water, 3)

    return rainfall_series, water_level_series


def prepare_sequences(rainfall, water_level, seq_len=SEQUENCE_LENGTH):
    """
    Transforms time series into sliding windows:
    X: shape (N, seq_len, 2) -> past rainfall & water levels
    y: shape (N, 1) -> next step water level
    """
    num_samples = len(rainfall) - seq_len
    X = np.zeros((num_samples, seq_len, 2))
    y = np.zeros((num_samples, 1))

    for i in range(num_samples):
        window_rain = rainfall[i : i + seq_len]
        window_water = water_level[i : i + seq_len]
        X[i] = np.column_stack([window_rain, window_water])
        y[i] = water_level[i + seq_len]

    return X, y


def train_flood_lstm():
    print("=" * 60)
    print("  RAINFALL-RUNOFF LSTM MODEL TRAINING PIPELINE")
    print("=" * 60)

    # 1. Generate Hydrological Data
    print("\n1. Generating synthetic hydrological time-series (catchment runoff)...")
    rainfall, water_level = generate_hydrological_data(num_steps=5000)
    print(f"   Total timesteps: {len(rainfall)}")
    print(f"   Rainfall range: {rainfall.min():.1f} mm to {rainfall.max():.1f} mm")
    print(f"   Water level range: {water_level.min():.2f} m to {water_level.max():.2f} m")

    # 2. Sequence Windowing
    seq_len = SEQUENCE_LENGTH
    X, y = prepare_sequences(rainfall, water_level, seq_len=seq_len)
    
    # 3. Train/Validation/Test Split (70% train, 15% val, 15% test)
    total_samples = len(X)
    train_size = int(0.70 * total_samples)
    val_size = int(0.15 * total_samples)
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size : train_size + val_size], y[train_size : train_size + val_size]
    X_test, y_test = X[train_size + val_size :], y[train_size + val_size :]

    # 4. Normalization Statistics (computed on train set only)
    train_rain = X_train[:, :, 0]
    train_water = X_train[:, :, 1]
    
    scaler_params = {
        "rain_mean": float(np.mean(train_rain)),
        "rain_std": float(np.std(train_rain)),
        "water_mean": float(np.mean(train_water)),
        "water_std": float(np.std(train_water)),
        "seq_len": seq_len
    }

    # Normalize data
    def normalize_x(data):
        norm = np.copy(data)
        norm[:, :, 0] = (norm[:, :, 0] - scaler_params["rain_mean"]) / scaler_params["rain_std"]
        norm[:, :, 1] = (norm[:, :, 1] - scaler_params["water_mean"]) / scaler_params["water_std"]
        return norm

    def normalize_y(targets):
        return (targets - scaler_params["water_mean"]) / scaler_params["water_std"]

    X_train_norm = normalize_x(X_train)
    y_train_norm = normalize_y(y_train)
    X_val_norm = normalize_x(X_val)
    y_val_norm = normalize_y(y_val)
    X_test_norm = normalize_x(X_test)
    y_test_norm = normalize_y(y_test)

    # 5. PyTorch Tensors & DataLoaders
    train_dataset = TensorDataset(torch.tensor(X_train_norm, dtype=torch.float32),
                                  torch.tensor(y_train_norm, dtype=torch.float32))
    val_dataset = TensorDataset(torch.tensor(X_val_norm, dtype=torch.float32),
                                torch.tensor(y_val_norm, dtype=torch.float32))

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    # 6. Initialize Model, Loss, Optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n2. Initializing LSTM model on: {device}")
    model = FloodLSTM(input_dim=2, hidden_dim=64, num_layers=2, output_dim=1, dropout=0.2).to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

    # 7. Training Loop
    epochs = 35
    best_val_loss = float("inf")
    best_weights = None

    print(f"\n3. Training LSTM for {epochs} epochs...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(batch_x)

        train_loss /= len(train_dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                preds = model(batch_x)
                loss = criterion(preds, batch_y)
                val_loss += loss.item() * len(batch_x)
        val_loss /= len(val_dataset)

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_weights = model.state_dict().copy()

        if epoch % 5 == 0 or epoch == 1:
            print(f"   Epoch [{epoch:02d}/{epochs:02d}] - Train Loss: {train_loss:.5f} | Val Loss: {val_loss:.5f}")

    # Load best weights
    model.load_state_dict(best_weights)

    # 8. Test Set Evaluation
    print("\n4. Evaluating Model on Unseen Test Set...")
    model.eval()
    with torch.no_grad():
        test_inputs = torch.tensor(X_test_norm, dtype=torch.float32).to(device)
        test_preds_norm = model(test_inputs).cpu().numpy()
        test_preds = (test_preds_norm * scaler_params["water_std"]) + scaler_params["water_mean"]

    rmse = math.sqrt(mean_squared_error(y_test, test_preds))
    mae = mean_absolute_error(y_test, test_preds)
    r2 = r2_score(y_test, test_preds)

    print(f"   [Test Results]")
    print(f"   - RMSE : {rmse:.4f} meters")
    print(f"   - MAE  : {mae:.4f} meters")
    print(f"   - R2   : {r2 * 100:.2f}%")

    # 9. Save Artifacts
    model_save_path = "flood_lstm_model.pth"
    scaler_save_path = "scaler_params.json"
    
    torch.save(model.state_dict(), model_save_path)
    with open(scaler_save_path, "w") as f:
        json.dump(scaler_params, f, indent=4)

    print(f"\n5. Successfully saved:")
    print(f"   - Model weights -> {os.path.abspath(model_save_path)}")
    print(f"   - Scaler params -> {os.path.abspath(scaler_save_path)}")
    print("=" * 60)


if __name__ == "__main__":
    train_flood_lstm()
