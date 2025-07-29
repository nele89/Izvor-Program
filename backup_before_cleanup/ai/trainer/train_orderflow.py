import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from logs.logger import log

# Putanje
MODEL_PATH = os.path.join("ai", "models", "orderflow_model.pkl")
SCALER_PATH = os.path.join("ai", "models", "orderflow_scaler.pkl")

def label_orderflow(df, threshold=0.0015):
    close = df["close"].values
    labels = [1]  # Neutral za prvu svećicu
    for i in range(1, len(close)):
        delta = (close[i] - close[i - 1]) / close[i - 1]
        if delta > threshold:
            labels.append(2)  # BUY
        elif delta < -threshold:
            labels.append(0)  # SELL
        else:
            labels.append(1)  # HOLD
    return labels

def train_orderflow_model(df):
    try:
        df = df.dropna()

        FEATURES = [
            'bid', 'ask', 'spread', 'volume',
            'rsi', 'macd', 'ema10', 'ema30',
            'adx', 'stochastic', 'cci', 'gold_trend'
        ]

        for f in FEATURES + ['close']:
            if f not in df.columns:
                raise ValueError(f"❌ Nedostaje kolona: {f}")

        df['orderflow_label'] = label_orderflow(df)

        X = df[FEATURES].values
        y = np.array(df['orderflow_label'])

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            class_weight="balanced"
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, target_names=["SELL", "HOLD", "BUY"])
        log.info("📊 Izveštaj tačnosti:\n" + report)

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)

        log.info("✅ Order Flow model uspešno treniran i sačuvan.")

    except Exception as e:
        log.error(f"❌ Greška u treniranju Order Flow modela: {e}")
