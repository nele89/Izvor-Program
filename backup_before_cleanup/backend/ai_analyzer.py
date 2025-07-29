import pandas as pd
import pickle
from logs.logger import log

MODEL_TYPE = "simple"  # može se kasnije proširiti na različite tipove

def train_model(df):
    """
    Trening simple modela - primer: linearna regresija, dummy logic itd.
    Očekuje da df ima kolone: 'open', 'high', 'low', 'close', 'volume'
    Prilagoditi ovu funkciju za složeniji AI po potrebi.
    """
    from sklearn.linear_model import LinearRegression
    import numpy as np

    # Dummy primer: predviđa 'close' na osnovu 'open', 'high', 'low', 'volume'
    features = ['open', 'high', 'low', 'volume']
    if not all(f in df.columns for f in features + ['close']):
        log.error("❌ Nedostaju potrebne kolone za trening modela!")
        raise ValueError("Nedostaju potrebne kolone za trening modela.")
    X = df[features].fillna(0)
    y = df['close'].fillna(0)
    model = LinearRegression()
    model.fit(X, y)
    return model

def save_model(model, path):
    with open(path, "wb") as f:
        pickle.dump(model, f)

def load_model(path):
    with open(path, "rb") as f:
        return # WARNING: Replaced unsafe pickle.load()
    # pickle.load(f)

def predict_with_model(model, features_dict):
    """
    features_dict: dict sa ključevima 'open', 'high', 'low', 'volume'
    """
    import numpy as np
    X = pd.DataFrame([features_dict])
    result = model.predict(X)[0]
    return result

def analyze_new_data(df, model):
    """
    Analizira DataFrame pomoću modela i vraća predikcije kao listu.
    """
    features = ['open', 'high', 'low', 'volume']
    X = df[features].fillna(0)
    predictions = model.predict(X)
    return predictions
