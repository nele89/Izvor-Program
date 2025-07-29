import os
import joblib
import torch
import numpy as np
import pandas as pd
from logs.logger import get_model_logger

log = get_model_logger("volume")

# Putanje do modela i skalera
MODEL_PATH = os.path.join("ai", "models", "volume_lstm.pt")
SCALER_PATH = os.path.join("ai", "models", "volume_scaler.pkl")

LOOKBACK = 120

FEATURES = [
    'open', 'high', 'low', 'close', 'volume',
    'rsi', 'macd', 'ema10', 'ema30',
    'adx', 'stochastic', 'cci',
    'spread', 'gold_trend'
]

class VolumeLSTM(torch.nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(VolumeLSTM, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def prepare_input(df):
    scaler = joblib.load(SCALER_PATH)
    df = df[FEATURES].fillna(0)
    scaled = scaler.transform(df.values)

    X = []
    for i in range(len(scaled) - LOOKBACK):
        X.append(scaled[i:i + LOOKBACK])
    if not X:
        raise ValueError("Nema dovoljno podataka za predikciju (potrebno barem 120 redova).")

    return torch.tensor(np.array(X), dtype=torch.float32)

def predict_volume(df):
    try:
        model = VolumeLSTM(input_size=len(FEATURES))
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()

        X_input = prepare_input(df)

        with torch.no_grad():
            prediction = model(X_input).numpy().flatten()[-1]

        log.info(f"📊 Predikcija volumena: {prediction}")
        return prediction

    except Exception as e:
        log.error(f"❌ Greška u predikciji volumena: {e}")
        return None
