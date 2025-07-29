# utils/histdata_converter.py

import os
import pandas as pd
from datetime import datetime
from logs.logger import log

RAW_FOLDER = os.path.join("data", "histdata")
OUT_FOLDER = os.path.join("data", "ohlc")
os.makedirs(OUT_FOLDER, exist_ok=True)

def convert_histdata_csv_to_ohlc():
    log.info("🔁 Pokrećem konverziju HistData CSV fajlova u OHLC...")
    
    files = [f for f in os.listdir(RAW_FOLDER) if f.endswith("_formatted.csv")]
    if not files:
        log.warning("⚠️ Nema .csv fajlova za konverziju u data/histdata/")
        return

    for file in files:
        try:
            full_path = os.path.join(RAW_FOLDER, file)
            df = pd.read_csv(full_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)

            # Resample to 1-minute OHLC
            ohlc = df.resample("1min").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()

            symbol = file.split("_")[0]
            output_file = os.path.join(OUT_FOLDER, f"{symbol}_M1.csv")
            ohlc.reset_index().to_csv(output_file, index=False)
            log.info(f"✅ Konvertovano: {file} ➜ {output_file}")

        except Exception as e:
            log.warning(f"❌ Greška pri konverziji {file}: {e}")

    log.info("🌟 Zavšena konverzija svih HistData fajlova.")

def convert_all_histdata():
    convert_histdata_csv_to_ohlc()
