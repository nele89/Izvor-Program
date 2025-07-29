import os
import joblib
import torch
import numpy as np
import pandas as pd
from logs.logger import get_model_logger

log = get_model_logger("volatility")

MODEL_PATH = os.path.join("ai", "models", "volatility_cnn.pt")
SCALER_PATH = os.path.join("ai", "models", "volatility_scaler.pkl")
LOOKBACK = 120

FEATURES = [
    'open', 'high', 'low', 'close', 'volume',
    'spread', 'rsi', 'macd', 'adx'
]

LABEL_MAP = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH"
}

class CNNModel(torch.nn.Module):
    def __init__(self, input_shape, num_classes=3):
        super(CNNModel, self).__init__()
        self.conv1 = torch.nn.Conv1d(in_channels=input_shape[1], out_channels=32, kernel_size=3)
        self.pool = torch.nn.MaxPool1d(kernel_size=2)
        conv_output_size = (input_shape[0] - 2) // 2
        self.flatten = torch.nn.Flatten()
        self.dropout = torch.nn.Dropout(0.3)
        self.fc = torch.nn.Linear(32 * conv_output_size, num_classes)

    def forward(self, x):
        x = x.permute(0, 2, 1)  # [batch, channels, time]
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.flatten(x)
        x = self.dropout(x)
        return self.fc(x)

def prepare_input(df):
    for col in FEATURES:
        if col not in df.columns:
            raise ValueError(f"Nedostaje kolona: {col}")

    scaler = joblib.load(SCALER_PATH)
    df = df[FEATURES].fillna(0)
    scaled = scaler.transform(df.values)

    X = []
    for i in range(len(scaled) - LOOKBACK):
        X.append(scaled[i:i+LOOKBACK])

    if not X:
        raise ValueError("❌ Nema dovoljno redova za volatilnost predikciju (minimum 120).")

    return torch.tensor(np.array(X), dtype=torch.float32)

def predict_volatility(df):
    try:
        input_shape = (LOOKBACK, len(FEATURES))
        model = CNNModel(input_shape=input_shape)
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()

        X_input = prepare_input(df)

        with torch.no_grad():
            logits = model(X_input)
            prediction = torch.argmax(logits, dim=1).numpy()[-1]
            return LABEL_MAP.get(int(prediction), "UNKNOWN")

    except Exception as e:
        log.error(f"❌ Greška u predikciji volatilnosti: {e}")
        return None
