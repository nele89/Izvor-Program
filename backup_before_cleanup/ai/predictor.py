import os
import joblib
import numpy as np
from logs.logger import log
from utils.paths import MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        log.warning("⚠️ AI model nije pronađen.")
        return None

    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju modela: {e}")
        return None

def predict_trade(**kwargs):
    model = load_model()
    if model is None:
        return None

    try:
        feature_order = [
            "rsi", "macd", "ema_diff", "volume",
            "spread", "volatility", "dxy_value",
            "us30_trend", "spx500_trend"
        ]
        input_data = np.array([[kwargs.get(feat, 0) for feat in feature_order]])
        prediction = model.predict(input_data)[0]
        return prediction
    except Exception as e:
        log.error(f"❌ Greška pri predikciji: {e}")
        return None
