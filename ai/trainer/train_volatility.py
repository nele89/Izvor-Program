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
log = get_model_logger("volatility")

# Putanje
MODEL_PATH = os.path.join("ai", "models", "volatility_cnn.pt")
SCALER_PATH = os.path.join("ai", "models", "volatility_scaler.pkl")

LOOKBACK = 120
EPOCHS = 10
BATCH_SIZE = 32

class CNN1DModel(nn.Module):
    def __init__(self, input_channels=1):
        super(CNN1DModel, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=input_channels, out_channels=32, kernel_size=3)
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32 * ((LOOKBACK - 2) // 2), 64)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.flatten(x)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

def create_sequences(data, lookback):
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    return np.array(X), np.array(y)

def train_volatility_model(df):
    try:
        if "volume" not in df.columns:
            raise ValueError("Nedostaje kolona 'volume'")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        data = df["volume"].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        joblib.dump(scaler, SCALER_PATH)

        X, y = create_sequences(data_scaled, LOOKBACK)
        X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)  # (batch, channels, length)
        y_tensor = torch.tensor(y, dtype=torch.float32)

        dataset = TensorDataset(X_tensor, y_tensor)

        # Trening/validacija podela
        val_size = int(0.1 * len(dataset))
        train_size = len(dataset) - val_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

        model = CNN1DModel().to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(EPOCHS):
            model.train()
            train_loss = 0.0
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs.squeeze(), y_batch)
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
                    loss = criterion(outputs.squeeze(), y_batch)
                    val_loss += loss.item()

            log.info(f"[Epoch {epoch + 1}] Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")

        torch.save(model.state_dict(), MODEL_PATH)
        log.info("✅ CNN model za volatilnost uspešno treniran i sačuvan.")

    except Exception as e:
        log.error(f"❌ Greška u treniranju volatility modela: {e}")
