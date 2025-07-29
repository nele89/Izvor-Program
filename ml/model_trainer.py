import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

def train_model(df):
    df = df.copy()

    # 🎯 Definiši cilj
    df['target'] = df['close'].shift(-1) > df['close']
    df['target'] = df['target'].astype(int)

    # 📊 Kolone koje očekujemo da već postoje
    features = ['rsi', 'macd', 'macd_signal', '%K', '%D', 'tenkan_sen', 'kijun_sen', 'adx']

    # ✅ Provera da li sve kolone postoje
    for col in features:
        if col not in df.columns:
            raise ValueError(f"Nedostaje kolona '{col}' u DataFrame. Prvo izračunaj sve tehničke indikatore.")

    # ❌ Ukloni redove sa nedostajućim vrednostima
    df = df.dropna(subset=features + ['target'])

    # 🎓 Treniraj model
    X = df[features]
    y = df['target']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 💾 Sačuvaj model
    joblib.dump(model, 'ml/trained_model.pkl')
    print("✅ Model je sačuvan kao ml/trained_model.pkl")
