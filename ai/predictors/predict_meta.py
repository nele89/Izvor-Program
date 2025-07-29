import os
import pandas as pd
import joblib
from logs.logger import log

# Putanja do sačuvanog modela
MODEL_PATH = os.path.join("ai", "models", "meta_model.pkl")

# Mapa za interpretaciju izlaza modela (klasa)
LABEL_MAP = {
    0: "SELL",
    1: "HOLD",
    2: "BUY"
}

REQUIRED_COLUMNS = [
    'trend_signal', 'volatility_signal', 'sentiment_signal', 'orderflow_signal'
]

def predict_meta_signal(df):
    try:
        # Provera da li svi potrebni inputi postoje
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Nedostaje kolona: {col}")

        latest_row = df[REQUIRED_COLUMNS].tail(1)
        if latest_row.empty:
            log.warning("⚠️ Nema dovoljno podataka za meta predikciju.")
            return None

        # Učitavanje modela
        model = joblib.load(MODEL_PATH)

        # Predikcija
        prediction = model.predict(latest_row.values)[0]
        signal = LABEL_MAP.get(prediction, "UNKNOWN")

        log.info(f"🤖 Meta-model predikcija: {signal} (class={prediction})")
        return prediction  # 0, 1 ili 2

    except Exception as e:
        log.error(f"❌ Greška u meta predikciji: {e}")
        return None
