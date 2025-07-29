import os
import sys
import pandas as pd
from datetime import datetime
import threading

sys.path.append(os.path.abspath(os.path.join(os.getcwd())))
from logs.logger import log

PARQUET_INPUT = os.path.join("data", "dukascopy", "trade_history.parquet")
OUTPUT_DIR = os.path.join("data", "dukascopy", "parquet_resampled")
START_DATE = datetime(2010, 1, 1)
ALLOWED_SYMBOLS = ["XAUUSD"]

ALLOWED_TIMEFRAMES = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "M30": "30min",
    "H1": "1H"
}

# === MODE: skalping ili daily ===
MODE = "scalping"  # ili "daily"

TIMEFRAME_MODES = {
    "scalping": ["M1", "M5", "M15"],
    "daily": ["M15", "M30", "H1"]
}
SELECTED_TIMEFRAMES = {tf: ALLOWED_TIMEFRAMES[tf] for tf in TIMEFRAME_MODES[MODE] if tf in ALLOWED_TIMEFRAMES}

conversion_in_progress = False

def _conversion_status_reporter():
    global conversion_in_progress
    while conversion_in_progress:
        log.info("🔄 Konverzija fajlova u toku...")
        threading.Event().wait(15)

def resample_df(df, rule):
    df = df.copy()
    if "time" not in df.columns:
        raise ValueError("Nema kolone 'time' u DataFrame-u!")

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])
    df = df.sort_values("time")
    df.set_index("time", inplace=True)

    if "volume" not in df.columns:
        df["volume"] = 0

    ohlc_dict = {
        "bid": "ohlc",
        "volume": "sum"
    }

    try:
        resampled = df.resample(rule).agg(ohlc_dict)
    except Exception as e:
        raise RuntimeError(f"Greška pri resamplovanju: {e}")

    resampled.columns = [
        f"{col[0]}_{col[1]}" if col[1] != "" else col[0]
        for col in resampled.columns.values
    ]

    for col in ["open", "high", "low", "close"]:
        resampled[col] = resampled.get(f"bid_{col}", None)
    resampled["volume"] = resampled.get("volume_sum", 0)

    resampled.dropna(subset=["close"], inplace=True)
    resampled.reset_index(inplace=True)

    resampled["ema10"] = resampled["close"].ewm(span=10, adjust=False).mean()
    resampled["ema30"] = resampled["close"].ewm(span=30, adjust=False).mean()
    resampled["gold_trend"] = (
        (resampled["ema10"] > resampled["ema30"]).astype(int) -
        (resampled["ema10"] < resampled["ema30"]).astype(int)
    )

    return resampled

def convert_parquet_by_days(parquet_path=PARQUET_INPUT, symbol="XAUUSD", timeframes=None):
    global conversion_in_progress
    if conversion_in_progress:
        log.warning("⏳ Konverzija je već u toku – preskačem dupli poziv.")
        return
    conversion_in_progress = True
    threading.Thread(target=_conversion_status_reporter, daemon=True).start()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timeframes = timeframes or SELECTED_TIMEFRAMES

    try:
        df = pd.read_parquet(parquet_path, columns=["time", "bid", "volume"])
        if "time" not in df.columns:
            log.warning(f"⚠️ Parquet {parquet_path} nema kolonu 'time'.")
            conversion_in_progress = False
            return
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
        df = df[df["time"] >= START_DATE]

        if df.empty:
            log.warning(f"⚠️ Parquet {parquet_path} je prazan nakon filtriranja.")
            conversion_in_progress = False
            return

        df["date"] = df["time"].dt.date
        unique_days = df["date"].unique()

        for tf_name, tf_rule in timeframes.items():
            out_path = os.path.join(OUTPUT_DIR, f"{symbol}_{tf_name}.parquet")
            if os.path.exists(out_path):
                os.remove(out_path)  # počni iz početka

            log.info(f"⏳ Počinjem chunkovano resamplovanje {len(unique_days)} dana za {tf_name}...")

            result_list = []
            for i, day in enumerate(unique_days):
                df_day = df[df["date"] == day].copy()
                if df_day.empty:
                    continue
                try:
                    resampled = resample_df(df_day, tf_rule)
                    if not resampled.empty:
                        result_list.append(resampled)
                    log.info(f"✔️ ({i+1}/{len(unique_days)}) Resamplovan dan {day} ({len(df_day)} tikova → {len(resampled)} redova)")
                except Exception as e:
                    log.warning(f"⚠️ Greška za dan {day} ({tf_name}): {e}")

                # Zapisuj povremeno na disk (npr. na svakih 10 dana ili na kraju)
                if (i+1) % 10 == 0 or (i+1) == len(unique_days):
                    if result_list:
                        full_result = pd.concat(result_list, ignore_index=True)
                        full_result.to_parquet(out_path, index=False)
                        result_list = []

            log.info(f"✅ Chunkovano konvertovan timeframe {tf_name}: {out_path}")

    except Exception as e:
        log.error(f"❌ Greška u konverziji {parquet_path}: {e}")

    conversion_in_progress = False

def convert_all_ticks():
    convert_parquet_by_days(PARQUET_INPUT, "XAUUSD", SELECTED_TIMEFRAMES)

if __name__ == "__main__":
    convert_all_ticks()
