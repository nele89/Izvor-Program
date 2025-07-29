import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
from logs.logger import log

FEATURES_PARQUET = os.path.join("data", "trade_features.parquet")
_last_vola_state = None  # Globalna promenljiva za GUI lampicu

def fetch_historical_data_parquet(limit: int = 500) -> pd.DataFrame:
    """
    Učitaj zadnjih 'limit' zapisa za volume i volatility iz Parquet fajla.
    """
    try:
        if not os.path.exists(FEATURES_PARQUET):
            log.error(f"❌ Parquet fajl NE POSTOJI: {FEATURES_PARQUET}")
            return pd.DataFrame()

        df = pd.read_parquet(FEATURES_PARQUET)
        for col in ["volume", "volatility"]:
            if col not in df.columns:
                log.error(f"❌ Kolona '{col}' NE POSTOJI u trade_features.parquet.")
                return pd.DataFrame()
        # sortiranje po "trade_id" ili "timestamp" ako postoji
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")
        elif "trade_id" in df.columns:
            df = df.sort_values("trade_id")
        else:
            df = df.reset_index(drop=True)
        return df[["volume", "volatility"]].tail(limit).reset_index(drop=True)
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju podataka za volume/volatility predikciju: {e}")
        return pd.DataFrame()

def predict_volume_volatility():
    """
    Predviđa sledeće vrednosti volume i volatility koristeći linearnu regresiju na zadnjih 5 zapisa.
    """
    df = fetch_historical_data_parquet()
    if df.empty or len(df) < 30:
        log.warning("⚠️ Nema dovoljno podataka za predikciju volume/volatility.")
        return None, None, "Nema dovoljno podataka za predikciju."

    try:
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df[["volume", "volatility"]])

        X, y_vol, y_vola = [], [], []
        for i in range(len(df) - 5):
            X.append(features_scaled[i:i+5].flatten())
            y_vol.append(features_scaled[i+5][0])   # volume
            y_vola.append(features_scaled[i+5][1])  # volatility

        X = np.array(X)
        y_vol = np.array(y_vol)
        y_vola = np.array(y_vola)

        if X.shape[0] < 5:
            log.warning("⚠️ Nema dovoljno uzastopnih zapisa za treniranje linearnog modela!")
            return None, None, "Premalo uzastopnih podataka za predikciju."

        model_vol = LinearRegression().fit(X, y_vol)
        model_vola = LinearRegression().fit(X, y_vola)

        last_sequence = features_scaled[-5:].flatten().reshape(1, -1)
        pred_vol_scaled = model_vol.predict(last_sequence)[0]
        pred_vola_scaled = model_vola.predict(last_sequence)[0]

        predicted_scaled = np.array([[pred_vol_scaled, pred_vola_scaled]])
        predicted_original = scaler.inverse_transform(predicted_scaled)

        pred_volume, pred_volatility = predicted_original[0]
        return round(pred_volume, 2), round(pred_volatility, 3), None
    except Exception as e:
        log.error(f"❌ Greška u volume/volatility predikciji: {e}")
        return None, None, "Greška u predikciji modela."

def predict_next_volatility_and_volume(symbol_data=None):
    """
    Kategorizuje sledeći volatility na low/medium/high za GUI lampicu.
    """
    _, volatility, err = predict_volume_volatility()
    if err:
        log.warning(f"⚠️ {err}")
        return None

    if volatility is None:
        return None

    # Kategorije možeš prilagoditi potrebama svog sistema
    if volatility < 0.5:
        state = "low"
    elif 0.5 <= volatility < 1.5:
        state = "medium"
    else:
        state = "high"

    set_last_volatility_state(state)
    return state

def get_last_volatility_state():
    return _last_vola_state

def set_last_volatility_state(state):
    global _last_vola_state
    _last_vola_state = state

if __name__ == "__main__":
    volume, volatility, err = predict_volume_volatility()
    if err:
        print("⚠️", err)
    else:
        print(f"📊 Predikcija: Volume={volume}, Volatility={volatility}")

    stanje = predict_next_volatility_and_volume()
    print(f"🟡 Volatilnost kategorizovana kao: {stanje}")
