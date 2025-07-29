import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from logs.logger import log

# Putanja
MODEL_PATH = os.path.join("ai", "models", "meta_model.pkl")

def train_meta_model(df):
    """
    Treniranje meta-modela koji kombinuje signale iz više modela.
    Očekuje kolone:
    ['trend_signal', 'volatility_signal', 'sentiment_signal', 'orderflow_signal', 'final_label']
    """
    try:
        expected_columns = [
            'trend_signal', 'volatility_signal',
            'sentiment_signal', 'orderflow_signal',
            'final_label'
        ]
        for col in expected_columns:
            if col not in df.columns:
                raise ValueError(f"❌ Nedostaje kolona: {col}")

        df = df.dropna(subset=expected_columns)

        X = df[['trend_signal', 'volatility_signal', 'sentiment_signal', 'orderflow_signal']]
        y = df['final_label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            class_weight="balanced",
            random_state=42
        )
        model.fit(X_train, y_train)

        # Evaluacija
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, target_names=["SELL", "HOLD", "BUY"])
        log.info("📊 Meta-model izveštaj tačnosti:\n" + report)

        # Čuvanje
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        log.info("✅ Meta-model uspešno treniran i sačuvan.")

    except Exception as e:
        log.error(f"❌ Greška u treniranju meta-modela: {e}")
