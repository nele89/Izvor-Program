import os
import pandas as pd
from datetime import datetime
from logs.logger import log

SOURCE_FOLDER = os.path.join("data", "dukascopy")
OUTPUT_FOLDER = os.path.join("data", "dukascopy_converted")
TIMEFRAMES = {
    "M1": "1min",
    "M5": "5min",
    "H1": "1H",
    "D1": "1D"
}

def convert_ticks_to_ohlcv(df, timeframe):
    df = df.copy()
    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df[~df.index.duplicated(keep='first')]

    resampled = df.resample(TIMEFRAMES[timeframe]).agg({
        "ask": ["first", "max", "min", "last"],
        "bid": ["first", "max", "min", "last"],
        "volume": "sum"
    })

    resampled.columns = [
        "ask_open", "ask_high", "ask_low", "ask_close",
        "bid_open", "bid_high", "bid_low", "bid_close",
        "volume"
    ]
    resampled.reset_index(inplace=True)
    # Ukloni prazne periode (npr. no trading)
    resampled.dropna(inplace=True)
    return resampled

def convert_symbol(symbol):
    input_dir = os.path.join(SOURCE_FOLDER, symbol)
    if not os.path.exists(input_dir):
        log.warning(f"📁 Folder ne postoji: {input_dir}")
        return

    files = sorted([f for f in os.listdir(input_dir) if f.endswith(".csv")])
    all_ticks = []
    skipped = 0
    loaded = 0

    for file in files:
        path = os.path.join(input_dir, file)
        # Preskoči sumnjive male ili prazne fajlove
        if os.path.getsize(path) < 128:
            skipped += 1
            continue
        try:
            df = pd.read_csv(path, parse_dates=["time"])
            if len(df) == 0:
                skipped += 1
                continue
            all_ticks.append(df)
            loaded += 1
        except Exception as e:
            log.warning(f"⚠️ Ne mogu da pročitam: {file}: {e}")
            skipped += 1

    if not all_ticks:
        log.warning(f"📉 Nema validnih podataka za konverziju: {symbol}")
        return

    merged_df = pd.concat(all_ticks, ignore_index=True)
    merged_df = merged_df.sort_values("time")
    merged_df = merged_df.drop_duplicates(subset=["time"])

    for tf in TIMEFRAMES:
        tf_dir = os.path.join(OUTPUT_FOLDER, symbol)
        os.makedirs(tf_dir, exist_ok=True)
        ohlcv = convert_ticks_to_ohlcv(merged_df, tf)
        output_path = os.path.join(tf_dir, f"{symbol}_{tf}.csv")
        ohlcv.to_csv(output_path, index=False)
        log.info(f"📦 Konvertovano {symbol} -> {tf} ({len(ohlcv)} redova)")

    log.info(f"✅ {symbol}: Konverzija završena ({loaded} fajlova, {skipped} preskočeno)")

def convert_all_ticks():
    log.info("🔄 Pokrećem konverziju tick podataka u OHLCV vremenske okvire...")
    if not os.path.exists(SOURCE_FOLDER):
        log.warning("❌ Izvorni folder ne postoji.")
        return

    symbols = [d for d in os.listdir(SOURCE_FOLDER) if os.path.isdir(os.path.join(SOURCE_FOLDER, d))]
    for symbol in symbols:
        try:
            convert_symbol(symbol)
        except Exception as e:
            log.error(f"❌ Greska u konverziji za {symbol}: {e}")

    log.info("✅ Konverzija završena za sve simbole.")

if __name__ == "__main__":
    convert_all_ticks()
