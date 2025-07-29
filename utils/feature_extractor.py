import pandas as pd
import os
from utils.settings_handler import load_settings
from backend.mt5_connector import get_symbol_data
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from indicators.ema import calculate_ema

PARQUET_DIR = os.path.join("data", "features")
os.makedirs(PARQUET_DIR, exist_ok=True)

def extract_features():
    settings = load_settings()
    symbol = settings.get("symbol", "XAUUSD")
    timeframe = settings.get("timeframe", "M5")

    df = get_symbol_data(symbol, timeframe, bars=100)
    if df is None or df.empty:
        print("⚠️ Nema podataka za simbol:", symbol)
        return

    df["rsi"] = calculate_rsi(df["close"], period=14)
    df["macd"], df["macd_signal"] = calculate_macd(df["close"])
    df["ema_20"] = calculate_ema(df["close"], period=20)
    df["ema_50"] = calculate_ema(df["close"], period=50)
    df["ema_diff"] = df["ema_20"] - df["ema_50"]
    df["spread"] = df["ask"] - df["bid"] if "ask" in df and "bid" in df else 0
    df["volatility"] = df["high"] - df["low"]
    df["volume"] = df["tick_volume"] if "tick_volume" in df.columns else 0

    dxy = get_symbol_data("DXY", timeframe, bars=2)
    dxy_value = dxy["close"].iloc[-1] if dxy is not None else 0

    us30 = get_symbol_data("US30", timeframe, bars=2)
    us30_trend = 1 if us30 is not None and us30["close"].iloc[-1] > us30["close"].iloc[-2] else \
                 -1 if us30 is not None and us30["close"].iloc[-1] < us30["close"].iloc[-2] else 0

    spx = get_symbol_data("SPX500", timeframe, bars=2)
    spx500_trend = 1 if spx is not None and spx["close"].iloc[-1] > spx["close"].iloc[-2] else \
                   -1 if spx is not None and spx["close"].iloc[-1] < spx["close"].iloc[-2] else 0

    last_row = df.iloc[-1].copy()
    last_row["dxy_value"] = dxy_value
    last_row["us30_trend"] = us30_trend
    last_row["spx500_trend"] = spx500_trend

    save_cols = [
        "rsi", "macd", "ema_diff", "volume", "spread", "volatility",
        "dxy_value", "us30_trend", "spx500_trend"
    ]
    single_df = pd.DataFrame([last_row[save_cols]])

    parquet_path = os.path.join(PARQUET_DIR, f"{symbol}_{timeframe}_features.parquet")
    if os.path.exists(parquet_path):
        old_df = pd.read_parquet(parquet_path)
        single_df = pd.concat([old_df, single_df], ignore_index=True)
    single_df.to_parquet(parquet_path, index=False)
    print(f"✅ Features uspešno upisani u {parquet_path}")

if __name__ == "__main__":
    extract_features()
