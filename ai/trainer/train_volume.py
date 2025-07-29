import os
import torch
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from logs.logger import get_model_logger

# Logger
log = get_model_logger("volume")

# Putanje za čuvanje modela i skalera
MODEL_PATH = os.path.join("ai", "models", "volume_lstm.pt")
SCALER_PATH = os.path.join("ai", "models", "volume_scaler.pkl")

# Broj svećica unazad za treniranje
LOOKBACK = 120

class VolumeLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super(VolumeLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # samo zadnji output
        return out

def create_sequences(data, lookback):
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    return np.array(X), np.array(y)

def train_volume_model(df):
    try:
        if "volume" not in df.columns:
            raise ValueError("Nedostaje kolona 'volume' u DataFrame-u!")

        # Skaliranje podataka
        volume_data = df["volume"].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        volume_scaled = scaler.fit_transform(volume_data)
        joblib.dump(scaler, SCALER_PATH)

        # Kreiranje sekvenci
        X, y = create_sequences(volume_scaled, LOOKBACK)
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)

        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)

        # Model
        model = VolumeLSTM()
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        # Treniranje
        for epoch in range(10):
            model.train()
            epoch_loss = 0
            for X_batch, y_batch in loader:
                optimizer.zero_grad()
                output = model(X_batch)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            log.info(f"[Epoch {epoch+1}] Loss: {epoch_loss:.6f}")

        # Čuvanje modela
        torch.save(model.state_dict(), MODEL_PATH)
        log.info("✅ LSTM model za volumen uspešno treniran i sačuvan.")

    except Exception as e:
        log.error(f"❌ Greška u treniranju volume modela: {e}")
