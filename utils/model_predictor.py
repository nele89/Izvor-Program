import os
import joblib
import pandas as pd
from logs.logger import log
from utils.paths import MODEL_DIR

# ============= MOD SELEKCIJA =============
MODE = "scalping"  # ili "daily"

# Možeš koristiti posebne modele/feature-order po modu ako budeš želeo
MODEL_PATHS = {
    "scalping": os.path.join(MODEL_DIR, "model_scalping.pkl"),
    "daily": os.path.join(MODEL_DIR, "model_daily.pkl"),
}
MODEL_PATH = MODEL_PATHS.get(MODE, os.path.join(MODEL_DIR, "model.pkl"))

FEATURE_ORDERS = {
    "scalping": [
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
        "gold_trend"
    ],
    "daily": [
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
        "gold_trend"
    ]
}
FEATURE_ORDER = FEATURE_ORDERS[MODE]

def load_model():
    """Učitaj AI model sa diska."""
    if not os.path.exists(MODEL_PATH):
        log.warning(f"⚠️ AI model nije pronađen na putanji: {MODEL_PATH}")
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju modela: {e}")
        return None

def predict_trade(mode=MODE, **kwargs):
    """
    Vrati AI odluku (npr. 'BUY'/'SELL') za zadate indikatore.
    Svi feature-i moraju biti prosleđeni kao keyword argumenti.
    """
    model_path = MODEL_PATHS.get(mode, MODEL_PATH)
    feature_order = FEATURE_ORDERS.get(mode, FEATURE_ORDER)

    model = None
    if model_path != MODEL_PATH:
        if not os.path.exists(model_path):
            log.warning(f"⚠️ Model za mod '{mode}' nije pronađen: {model_path}")
        else:
            model = joblib.load(model_path)
    else:
        model = load_model()

    if model is None:
        return None

    # Provera broja feature-a koje model očekuje
    try:
        expected_features = model.n_features_in_
    except AttributeError:
        log.error("❌ Model nema atribut n_features_in_.")
        return None

    if expected_features != len(feature_order):
        log.error(f"❌ Model očekuje {expected_features} feature-a, ali definisano je {len(feature_order)}.")
        return None

    # Provera da li su svi feature-i prosleđeni
    missing = [f for f in feature_order if f not in kwargs]
    if missing:
        log.error(f"❌ Nedostaju feature-i za predikciju: {missing}")
        return None

    try:
        input_df = pd.DataFrame([{feat: float(kwargs[feat]) for feat in feature_order}])
        prediction = model.predict(input_df)[0]
        log.info(f"AI odluka ({mode}): {prediction}")
        return str(prediction)
    except Exception as e:
        log.error(f"❌ Greška pri predikciji: {e}")
        return None

# Primer testiranja modula (opciono)
if __name__ == "__main__":
    test_input = {
        "rsi": 45,
        "macd": 0.02,
        "ema10": 1911.2,
        "ema30": 1912.1,
        "close": 1911.3,
        "volume": 120000,
        "spread": 0.11,
        "adx": 25,
        "stochastic": 77,
        "cci": 110,
        "gold_trend": 1
    }
    print(predict_trade(**test_input))
