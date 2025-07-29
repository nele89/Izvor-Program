# engine/ai_input_formatter.py

import pandas as pd

def format_for_model(df):
    """
    Prima DataFrame sa indikatorima i vraća poslednji red kao ulazni vektor za AI model
    """
    if df is None or df.empty:
        return None

    latest = df.iloc[-1]

    features = {
        "close": latest.get("close", 0),
        "RSI": latest.get("RSI", 50),
        "MACD_Line": latest.get("MACD_Line", 0),
        "MACD_Hist": latest.get("MACD_Hist", 0),
        "Supertrend": int(latest.get("Supertrend", True)),
        "MA50": latest.get("MA50", latest.get("close", 0)),
        "MA200": latest.get("MA200", latest.get("close", 0)),
        "ATR": latest.get("ATR", 0),
    }

    return pd.DataFrame([features])
