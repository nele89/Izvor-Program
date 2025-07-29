import os
import pandas as pd
import numpy as np
import json
import shutil
import threading
from logs.logger import log  # koristi tvoj logger

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
ALLOWED_TIMEFRAMES = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "M30": "30min",
    "H1": "1H"
}
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

PARQUET_FILE = os.path.join("data", "dukascopy", "trade_history.parquet")
OUTPUT_DIR = os.path.join("data", "dukascopy", "parquet_resampled")
RESAMPLE_LOG = os.path.join("data", "dukascopy", "resample_log.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TIMEFRAMES = ALLOWED_TIMEFRAMES

# === Globalni lock i flag za resample ===
resample_lock = threading.Lock()
resample_in_progress = False


def load_resample_log():
    if os.path.exists(RESAMPLE_LOG):
        try:
            with open(RESAMPLE_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"⚠️ Greška pri učitavanju resample_log: {e}")
    return {}


def save_resample_log(log_data):
    try:
        if os.path.exists(RESAMPLE_LOG):
            shutil.copy2(RESAMPLE_LOG, RESAMPLE_LOG + ".bak")
        with open(RESAMPLE_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as ex:
        log.warning(f"❌ Ne mogu da upišem resample_log: {ex}")


def calc_indicators(df):
    # ... isti kao pre ...
    # (skraćeno za preglednost)
    out = df.copy()
    out['ema10'] = out['close'].ewm(span=10, adjust=False).mean()
    out['ema30'] = out['close'].ewm(span=30, adjust=False).mean()
    delta = out['close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = up.rolling(14).mean() / (down.rolling(14).mean() + 1e-9)
    out['rsi'] = 100 - (100 / (1 + rs))
    # ... ostali indikatori ...
    high, low, close = out['high'], out['low'], out['close']
    # implementirati ostale kao ranije
    return out


def make_labels(df, col="close", label_name="label"):
    df[label_name] = np.sign(df[col].shift(-1) - df[col])
    df[label_name] = df[label_name].fillna(0).astype(np.int8)
    return df


def resample_and_save(df, rule, out_path):
    # ovo ostaje isto
    df = df.copy()
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').resample(rule).agg({
        'bid': 'ohlc',
        'ask': 'ohlc',
        'volume': 'sum',
        'spread': 'mean'
    })
    df.columns = [f"{c[0]}_{c[1]}" for c in df.columns]
    df = df.dropna().reset_index()
    # postprocess close/high/low
    if 'bid_close' in df:
        df['close'] = df['bid_close']
        df['high'] = df.get('bid_high', df['close'])
        df['low'] = df.get('bid_low', df['close'])
    else:
        df['close'] = df['ask_close']
        df['high'] = df.get('ask_high', df['close'])
        df['low'] = df.get('ask_low', df['close'])
    df['spread'] = df.get('spread_mean', 0)
    df['volume'] = df.get('volume_sum', 0)
    df = calc_indicators(df)
    df = make_labels(df)
    df.to_parquet(out_path, index=False)
    log.info(f"✅ Snimljeno chunk: {out_path} ({len(df)} redova)")
    return {'rows': len(df), 'mtime': int(os.path.getmtime(out_path))}


def resample_parquet_all():
    global resample_in_progress
    with resample_lock:
        if resample_in_progress:
            log.warning("⏳ Resample je već u toku! Ignorišem dupli zahtev.")
            return
        resample_in_progress = True

        if not os.path.exists(PARQUET_FILE):
            log.error(f"❌ Master Parquet fajl NE postoji: {PARQUET_FILE}")
            resample_in_progress = False
            return

        log.info("🔄 Chunk-based resample M1/M5/M15/M30/H1...")

        # učitaj samo potrebne kolone
        cols = ['time','bid','ask','volume','spread']
        df_iter = pd.read_parquet(PARQUET_FILE, columns=cols)
        df_iter['time'] = pd.to_datetime(df_iter['time'], errors='coerce')
        df_iter = df_iter.dropna(subset=['time'])
        df_iter['date'] = df_iter['time'].dt.date
        dates = df_iter['date'].unique()

        res_log = load_resample_log()
        mt = int(os.path.getmtime(PARQUET_FILE))
        tf_meta = {}

        for tf, rule in TIMEFRAMES.items():
            out_path = os.path.join(OUTPUT_DIR, f"XAUUSD_{tf}.parquet")
            # izbriši stari
            if os.path.exists(out_path):
                os.remove(out_path)

            parts = []
            for d in dates:
                df_day = df_iter[df_iter['date']==d]
                if df_day.empty: continue
                parts.append(resample_and_save(df_day, rule, out_path + f".part_{d}"))

            # spoji sve chunk fajlove
            full = []
            for part in sorted(os.listdir(OUTPUT_DIR)):
                if part.startswith(f"XAUUSD_{tf}.parquet.part_"):
                    full.append(pd.read_parquet(os.path.join(OUTPUT_DIR, part)))
            if full:
                df_full = pd.concat(full, ignore_index=True)
                df_full.to_parquet(out_path, index=False)
                tf_meta[tf] = {'rows': len(df_full), 'mtime': int(os.path.getmtime(out_path))}
                # obriši part fajlove
                for part in os.listdir(OUTPUT_DIR):
                    if part.startswith(f"XAUUSD_{tf}.parquet.part_"):
                        os.remove(os.path.join(OUTPUT_DIR, part))

        # upisi log
        res_log['master_mtime'] = mt
        res_log['outputs'] = tf_meta
        save_resample_log(res_log)
        resample_in_progress = False


def resample_parquet_selected(selected):
    # analogno, samo za izabrane timeframe-ove
    pass

if __name__ == '__main__':
    resample_parquet_all()
