import os
import numpy as np
import pandas as pd
import joblib
from logs.logger import log

MODEL_PATH = os.path.join("ai", "models", "orderflow_model.pkl")
SCALER_PATH = os.path.join("ai", "models", "orderflow_scaler.pkl")

FEATURES = [
    'bid', 'ask', 'spread', 'volume',
    'rsi', 'macd', 'ema10', 'ema30',
    'adx', 'stochastic', 'cci',
    'gold_trend'
]

LABEL_MAP = {
    0: "SELL",
    1: "HOLD",
    2: "BUY"
}

def predict_orderflow(df):
    try:
        # Provera da li svi potrebni feature-i postoje
        for col in FEATURES:
            if col not in df.columns:
                raise ValueError(f"Nedostaje kolona: {col}")

        df = df.dropna(subset=FEATURES)
        if len(df) < 1:
            log.warning("⚠️ Nema dovoljno podataka za orderflow predikciju.")
            return None

        latest_row = df[FEATURES].tail(1)

        # Učitavanje modela i skalera
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

        X = scaler.transform(latest_row.values)
        prediction = model.predict(X)[0]
        signal = LABEL_MAP.get(prediction, "UNKNOWN")

        log.info(f"📊 OrderFlow predikcija: {signal} (class={prediction})")
        return prediction  # 0, 1 ili 2

    except Exception as e:
        log.error(f"❌ Greška u orderflow predikciji: {e}")
        return None
