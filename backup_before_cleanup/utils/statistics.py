import os
import pandas as pd
from datetime import datetime
from logs.logger import log

TRADE_HISTORY_PARQUET = os.path.join("data", "dukascopy", "trade_history.parquet")

def load_trade_history():
    if not os.path.exists(TRADE_HISTORY_PARQUET):
        log.warning(f"[STAT] Ne postoji fajl: {TRADE_HISTORY_PARQUET}")
        return pd.DataFrame()
    try:
        return pd.read_parquet(TRADE_HISTORY_PARQUET)
    except Exception as e:
        log.error(f"[STAT] Greška pri učitavanju trade_history.parquet: {e}")
        return pd.DataFrame()

def get_basic_stats(symbol=None):
    df = load_trade_history()
    if df.empty:
        log.warning("[STAT] Prazan trade_history DataFrame.")
        return {"total_trades": 0, "total_profit": 0, "avg_profit": 0, "max_profit": 0, "min_profit": 0}

    if symbol:
        df = df[df["symbol"] == symbol]

    return {
        "total_trades": len(df),
        "total_profit": float(df["profit"].sum()) if "profit" in df.columns else 0,
        "avg_profit": float(df["profit"].mean()) if "profit" in df.columns and not df.empty else 0,
        "max_profit": float(df["profit"].max()) if "profit" in df.columns and not df.empty else 0,
        "min_profit": float(df["profit"].min()) if "profit" in df.columns and not df.empty else 0
    }

def get_daily_profit(symbol=None):
    df = load_trade_history()
    if df.empty or "profit" not in df.columns:
        log.warning("[STAT] Nema podataka za dnevni profit.")
        return pd.DataFrame()
    if symbol:
        df = df[df["symbol"] == symbol]
    if "entry_time" in df.columns:
        df["date"] = pd.to_datetime(df["entry_time"]).dt.date
    else:
        log.warning("[STAT] Nema kolone entry_time.")
        return pd.DataFrame()
    return df.groupby("date")["profit"].sum().reset_index(name="daily_profit")

def get_stats_by_symbol():
    df = load_trade_history()
    if df.empty or "symbol" not in df.columns:
        log.warning("[STAT] Nema podataka po simbolima.")
        return []
    result = df.groupby("symbol").agg(
        total_trades=("symbol", "count"),
        total_profit=("profit", "sum"),
        avg_profit=("profit", "mean"),
        max_profit=("profit", "max"),
        min_profit=("profit", "min"),
    ).reset_index()
    return result.to_dict("records")

if __name__ == "__main__":
    print("Osnovne statistike svih trejdova:")
    print(get_basic_stats())
    print("Statistika po simbolu:")
    print(get_stats_by_symbol())
    print("Dnevni profit:")
    print(get_daily_profit())
