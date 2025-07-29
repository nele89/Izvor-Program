import pandas as pd
import os
from logs.logger import log

PARQUET_PATH = "data/positions.parquet"

def initialize_parquet():
    if not os.path.exists(PARQUET_PATH):
        df = pd.DataFrame(columns=[
            "id", "symbol", "open_time", "close_time",
            "volume", "open_price", "close_price", "profit"
        ])
        df.to_parquet(PARQUET_PATH, index=False)
        log.info("✅ Parquet fajl za pozicije inicijalizovan.")

def insert_position(symbol, open_time, volume, open_price):
    df = pd.read_parquet(PARQUET_PATH)
    new_id = (df["id"].max() + 1) if not df.empty else 1
    new_row = {
        "id": new_id,
        "symbol": symbol,
        "open_time": open_time,
        "close_time": None,
        "volume": volume,
        "open_price": open_price,
        "close_price": None,
        "profit": None
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_parquet(PARQUET_PATH, index=False)
    log.info(f"✅ Nova pozicija dodata za {symbol} (ID: {new_id})")

def update_position_close(id, close_time, close_price, profit):
    df = pd.read_parquet(PARQUET_PATH)
    idx = df.index[df["id"] == id]
    if not idx.empty:
        i = idx[0]
        df.at[i, "close_time"] = close_time
        df.at[i, "close_price"] = close_price
        df.at[i, "profit"] = profit
        df.to_parquet(PARQUET_PATH, index=False)
        log.info(f"📝 Pozicija ID {id} ažurirana (zatvorena).")
    else:
        log.warning(f"⚠️ Pozicija ID {id} nije pronađena!")

def get_all_positions():
    if not os.path.exists(PARQUET_PATH):
        return pd.DataFrame()
    df = pd.read_parquet(PARQUET_PATH)
    return df.sort_values("open_time", ascending=False)

if __name__ == "__main__":
    initialize_parquet()
    log.info("Parquet data/positions.parquet initialized.")
