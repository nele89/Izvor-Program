import os
import pandas as pd
from logs.logger import log
from utils.settings_handler import load_settings

DATA_PATHS = {
    "dukascopy": "data/dukascopy_converted",
    "histdata": "data/histdata"
}

def load_symbol_data(symbol: str, timeframe: str = "M1"):
    settings = load_settings()
    source = settings.get("data_source", "dukascopy").lower()
    base_path = DATA_PATHS.get(source)
    
    if not base_path:
        log.error(f"⛔ Nepoznat izvor podataka: {source}")
        return None

    file_path = None
    if source == "dukascopy":
        file_path = os.path.join(base_path, symbol, f"{symbol}_{timeframe}.csv")
    elif source == "histdata":
        possible_files = [
            os.path.join(base_path, f"{symbol}_{timeframe}_formatted.csv"),
            os.path.join(base_path, f"{symbol}_{timeframe}.csv"),
            os.path.join(base_path, f"{symbol}_{timeframe.upper()}_formatted.csv"),
            os.path.join(base_path, f"{symbol}_{timeframe.upper()}.csv"),
            os.path.join(base_path, f"{symbol}_{timeframe.lower()}_formatted.csv"),
            os.path.join(base_path, f"{symbol}_{timeframe.lower()}.csv"),
        ]
        file_path = next((p for p in possible_files if os.path.exists(p)), None)
        if not file_path:
            log.warning(f"📉 Nema CSV fajla za {symbol}/{timeframe} u {base_path}")
            return None
    else:
        log.error(f"❌ Nepodržan izvor podataka: {source}")
        return None

    if not file_path or not os.path.exists(file_path):
        log.warning(f"📉 Nema CSV fajla: {file_path}")
        return None

    try:
        df = pd.read_csv(file_path)

        time_columns = [col for col in df.columns if col.lower() in ("time", "timestamp", "datetime", "date")]
        if time_columns:
            time_col = time_columns[0]
            df["time"] = pd.to_datetime(df[time_col])
            df = df.sort_values("time").reset_index(drop=True)
        else:
            log.warning(f"⚠️ Nema vremenske kolone u fajlu: {file_path}")
            return None

        if "ema10" in df.columns and "ema30" in df.columns:
            df["gold_trend"] = (df["ema10"] > df["ema30"]).astype(int) - (df["ema10"] < df["ema30"]).astype(int)
        else:
            df["gold_trend"] = 0

        if df.empty:
            log.warning(f"⚠️ Učitani DataFrame je prazan: {file_path}")
            return None

        tmin, tmax = df["time"].min(), df["time"].max()
        log.info(f"✅ Učitano {len(df)} redova iz {file_path} [{tmin} - {tmax}]")
        return df

    except Exception as e:
        log.error(f"❌ Greška pri učitavanju podataka iz {file_path}: {e}")
        return None
