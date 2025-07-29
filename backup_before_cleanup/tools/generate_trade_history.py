import os
import pandas as pd
from datetime import datetime
import threading
from logs.logger import log

# Putanje
PARQUET_RESAMPLED_DIR = os.path.join("data", "dukascopy", "parquet_resampled")
TRADE_HISTORY_PARQUET = os.path.join("data", "dukascopy", "trade_history.parquet")

# LOCK i FLAG za obradu (koristi isto ime i u drugim delovima sistema za sigurnost!)
trade_history_lock = threading.Lock()
trade_history_in_progress = False

def load_and_merge_parquets():
    all_dfs = []
    for timeframe in ["M1", "M5", "H1"]:
        file_path = os.path.join(PARQUET_RESAMPLED_DIR, f"XAUUSD_{timeframe}.parquet")
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            df["timeframe"] = timeframe
            all_dfs.append(df)
        else:
            log.warning(f"⚠️ Nema fajla: {file_path}")
    if not all_dfs:
        log.error("❌ Nema resampled parquet fajlova za XAUUSD!")
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

def calculate_profit_and_duration(df):
    df = df.sort_values(["timeframe", "time"]).reset_index(drop=True)

    if "close" not in df.columns:
        log.error("❌ Nema kolone 'close' u podacima, ne mogu računati profit!")
        df["profit"] = 0
    else:
        df["profit"] = df["close"].diff().fillna(0)

    df["entry_time"] = df["time"]
    df["exit_time"] = df["time"].shift(-1)

    df["duration"] = (
        pd.to_datetime(df["exit_time"]) - pd.to_datetime(df["entry_time"])
    ).dt.total_seconds().fillna(0)

    if "position_type" not in df.columns:
        df["position_type"] = "buy"
    if "opened_by" not in df.columns:
        df["opened_by"] = "auto"
    if "outcome" not in df.columns:
        df["outcome"] = "unknown"

    df = df.drop(columns=["timeframe"], errors="ignore")
    return df

def generate_trade_history():
    global trade_history_in_progress
    with trade_history_lock:
        if trade_history_in_progress:
            log.warning("⏳ Generisanje trade_history je već u toku! Ignorišem dupli zahtev.")
            return
        trade_history_in_progress = True

        try:
            if not os.path.exists(PARQUET_RESAMPLED_DIR):
                log.error(f"❌ Folder sa resampled fajlovima ne postoji: {PARQUET_RESAMPLED_DIR}")
                trade_history_in_progress = False
                return

            df = load_and_merge_parquets()
            if df.empty:
                log.warning("⚠️ Učitani podaci su prazni.")
                trade_history_in_progress = False
                return

            df = calculate_profit_and_duration(df)

            wanted_columns = [
                "entry_time", "exit_time", "position_type", "close", "profit", "duration",
                "opened_by", "outcome"
            ]
            for col in wanted_columns:
                if col not in df.columns:
                    df[col] = None

            df = df[wanted_columns]
            df.to_parquet(TRADE_HISTORY_PARQUET, index=False)
            log.info(f"✅ trade_history.parquet uspešno kreiran sa {len(df)} redova.")
        finally:
            trade_history_in_progress = False

if __name__ == "__main__":
    generate_trade_history()
