import os
import joblib
import numpy as np
from logs.logger import log
from utils.paths import MODEL_DIR

MODEL_PATH = os.path.join(MODEL_DIR, "gold_model.pkl")  # ili "model.pkl" ako koristiš isti model

# 11 feature-a, redosled mora biti identičan kao u dataset-u i kodu modela
FEATURE_ORDER = [
    "rsi",
    "macd",
    "ema10",
    "ema30",
    "close",
    "volume",
    "spread",
    "adx",
    "stochastic",
    "cci",
    "gold_trend"   # <<<<<<<<<< DODATO!
]

def load_gold_model():
    if not os.path.exists(MODEL_PATH):
        log.warning("⚠️ Gold AI model nije pronađen.")
        return None
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju gold modela: {e}")
        return None

def predict_gold_trade(feature_dict):
    """
    feature_dict: dict sa tačno 11 ključ/feature parova (uključuje gold_trend)
    Primer: {"rsi": 45, ..., "gold_trend": 0}
    """
    model = load_gold_model()
    if model is None:
        return None

    try:
        # Napravi ulazni niz feature-a u tačnom redosledu
        x = np.array([feature_dict.get(feat, 0) for feat in FEATURE_ORDER], dtype=np.float32).reshape(1, -1)
    except Exception as e:
        log.error(f"❌ Greška pri pripremi feature-a za gold_trade: {e}")
        return None

    try:
        prediction = model.predict(x)
        return prediction[0]  # vraća prvu i jedinu vrednost predikcije
    except Exception as e:
        log.error(f"❌ Greška pri predikciji gold_trade: {e}")
        return None

# Primer poziva za testiranje
if __name__ == "__main__":
    features = {
        "rsi": 50,
        "macd": 0.1,
        "ema10": 18000000,
        "ema30": 12000000,
        "close": 2100000,
        "volume": 6e10,
        "spread": 0,
        "adx": 20,
        "stochastic": 70,
        "cci": 100,
        "gold_trend": 0     # OBAVEZNO
    }
    result = predict_gold_trade(features)
    print("Predikcija za gold_trade:", result)
