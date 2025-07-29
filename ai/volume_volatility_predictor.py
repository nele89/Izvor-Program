import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import os

MODEL_FOLDER = "ai/models"
VOL_MODEL_FILE = os.path.join(MODEL_FOLDER, "volatility_model.joblib")
VOLU_MODEL_FILE = os.path.join(MODEL_FOLDER, "volume_model.joblib")

os.makedirs(MODEL_FOLDER, exist_ok=True)

def extract_features(df):
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(window=10).std()
    df["volume"] = df["tick_volume"]
    df.dropna(inplace=True)
    return df[["volatility", "volume"]]

def label_data(df):
    # Volatility klasifikacija
    vol_thresholds = df["volatility"].quantile([0.33, 0.66]).values
    df["vol_class"] = pd.cut(df["volatility"],
                             bins=[-np.inf, vol_thresholds[0], vol_thresholds[1], np.inf],
                             labels=["low", "medium", "high"])

    # Volume klasifikacija
    volu_thresholds = df["volume"].quantile([0.33, 0.66]).values
    df["volu_class"] = pd.cut(df["volume"],
                              bins=[-np.inf, volu_thresholds[0], volu_thresholds[1], np.inf],
                              labels=["low", "medium", "high"])
    return df

def train_models(df):
    df = extract_features(df)
    df = label_data(df)

    X = df[["volatility", "volume"]].values

    y_vol = df["vol_class"].values
    y_volu = df["volu_class"].values

    vol_model = RandomForestClassifier(n_estimators=100)
    vol_model.fit(X, y_vol)
    dump(vol_model, VOL_MODEL_FILE)

    volu_model = RandomForestClassifier(n_estimators=100)
    volu_model.fit(X, y_volu)
    dump(volu_model, VOLU_MODEL_FILE)

    print("✅ AI modeli za volatility i volume su uspešno trenirani i sačuvani.")

def predict_volatility_volume(df):
    df = extract_features(df)
    latest = df.iloc[-1][["volatility", "volume"]].values.reshape(1, -1)

    vol_model = load(VOL_MODEL_FILE)
    volu_model = load(VOLU_MODEL_FILE)

    vol_pred = vol_model.predict(latest)[0]
    volu_pred = volu_model.predict(latest)[0]

    return vol_pred, volu_pred
