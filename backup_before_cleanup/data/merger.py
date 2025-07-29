# data/tools/merger.py

import os
import pandas as pd
from tqdm import tqdm
from logs.logger import log

SOURCE_DIR = os.path.join("data", "trading_data")
OUTPUT_DIR = os.path.join("data", "merged_data")
TIMEFRAMES = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "H1": "1H",
    "H4": "4H"
}

def load_tick_csv(file_path):
    try:
        df = pd.read_csv(file_path, parse_dates=["time"])
        df.set_index("time", inplace=True)
        return df
    except Exception as e:
        log.warning(f"⚠️ Ne mogu učitati fajl {file_path}: {e}")
        return None

def resample_ticks(df, tf_code):
    try:
        ohlc_dict = {
            "ask": "ohlc",
            "bid": "ohlc",
            "volume": "sum"
        }
        resampled = df.resample(tf_code).apply(ohlc_dict)
        resampled.columns = ['ask_open', 'ask_high', 'ask_low', 'ask_close',
                             'bid_open', 'bid_high', 'bid_low', 'bid_close', 'volume']
        resampled.dropna(inplace=True)

        # Dodaj prosek
        resampled["open"] = (resampled["ask_open"] + resampled["bid_open"]) / 2
        resampled["high"] = (resampled["ask_high"] + resampled["bid_high"]) / 2
        resampled["low"] = (resampled["ask_low"] + resampled["bid_low"]) / 2
        resampled["close"] = (resampled["ask_close"] + resampled["bid_close"]) / 2

        return resampled[["open", "high", "low", "close", "volume"]].reset_index()
    except Exception as e:
        log.error(f"❌ Greška pri resamplovanju: {e}")
        return None

def process_symbol(symbol):
    symbol_files = sorted([
        f for f in os.listdir(SOURCE_DIR)
        if f.startswith(symbol + "_") and f.endswith(".csv")
    ])

    if not symbol_files:
        log.warning(f"⚠️ Nema fajlova za simbol: {symbol}")
        return

    for tf_name, tf_code in TIMEFRAMES.items():
        all_chunks = []
        for file in tqdm(symbol_files, desc=f"{symbol} - {tf_name}"):
            df = load_tick_csv(os.path.join(SOURCE_DIR, file))
            if df is not None:
                resampled = resample_ticks(df, tf_code)
                if resampled is not None:
                    all_chunks.append(resampled)

        if all_chunks:
            final_df = pd.concat(all_chunks)
            out_dir = os.path.join(OUTPUT_DIR, symbol)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{symbol}_{tf_name}.csv")
            final_df.to_csv(out_path, index=False)
            log.info(f"✅ Sačuvan: {out_path} ({len(final_df)} redova)")

def main():
    log.info("📊 Pokrećem konverziju tick podataka u veće timeframe CSV fajlove...")

    symbols = set()
    for fname in os.listdir(SOURCE_DIR):
        if fname.endswith(".csv") and "_" in fname:
            symbols.add(fname.split("_")[0])

    for symbol in sorted(symbols):
        process_symbol(symbol)

    log.info("🏁 Završena konverzija svih simbola.")

if __name__ == "__main__":
    main()
