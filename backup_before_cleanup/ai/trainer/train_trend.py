import os
import torch
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split
from logs.logger import get_model_logger

# Logger
log = get_model_logger("trend")

# Putanje
MODEL_PATH = os.path.join("ai", "models", "trend_lstm.pt")
SCALER_PATH = os.path.join("ai", "models", "trend_scaler.pkl")

LOOKBACK = 120
EPOCHS = 10
BATCH_SIZE = 32

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(data, lookback):
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i+lookback])
        y.append(data[i+lookback])
    return np.array(X), np.array(y)

def train_trend_model(df):
    try:
        if "close" not in df.columns:
            raise ValueError("Nedostaje kolona 'close'")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        data = df["close"].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        joblib.dump(scaler, SCALER_PATH)

        X, y = create_sequences(data_scaled, LOOKBACK)
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)

        dataset = TensorDataset(X_tensor, y_tensor)

        # Split za trening i validaciju
        val_size = int(0.1 * len(dataset))
        train_size = len(dataset) - val_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

        model = LSTMModel().to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(EPOCHS):
            model.train()
            train_loss = 0.0
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Validacija
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                    outputs = model(X_batch)
                    loss = criterion(outputs, y_batch)
                    val_loss += loss.item()

            log.info(f"[Epoch {epoch+1}] Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")

        torch.save(model.state_dict(), MODEL_PATH)
        log.info("✅ LSTM model za trend uspešno treniran i sačuvan.")

    except Exception as e:
        log.error(f"❌ Greška u treniranju trend modela: {e}")
