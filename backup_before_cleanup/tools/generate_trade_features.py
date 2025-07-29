import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import threading

# Omogući import iz root foldera ako je potrebno
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from logs.logger import log
except ImportError:
    class DummyLog:
        def info(self, msg): print("[INFO]", msg)
        def warning(self, msg): print("[WARNING]", msg)
        def error(self, msg): print("[ERROR]", msg)
    log = DummyLog()

# Putanje do parquet fajlova
TRADE_HISTORY_PARQUET = os.path.join("data", "dukascopy", "trade_history.parquet")
TRADE_FEATURES_PARQUET = os.path.join("data", "dukascopy", "trade_features.parquet")

# Lock i flag za status procesa
trade_features_lock = threading.Lock()
trade_features_in_progress = False

def calculate_indicators(df):
    df = df.copy()

    # Popuni high, low, close ako ih nema
    for col in ['high', 'low', 'close']:
        if col not in df.columns:
            df[col] = df['close'] if 'close' in df.columns else 0

    # EMA indikatori
    df['ema10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema30'] = df['close'].ewm(span=30, adjust=False).mean()

    # RSI
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / (roll_down + 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2

    # ADX
    high = df['high']
    low = df['low']
    close = df['close']
    plus_dm = high.diff().clip(lower=0)
    minus_dm = -low.diff().clip(upper=0)
    tr1 = (high - low).abs()
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / (atr + 1e-9))
    minus_di = 100 * (minus_dm.rolling(14).mean() / (atr + 1e-9))
    adx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)).rolling(14).mean()
    df['adx'] = adx

    # Stochastic
    low_min = low.rolling(14).min()
    high_max = high.rolling(14).max()
    df['stochastic'] = 100 * ((close - low_min) / (high_max - low_min + 1e-9))

    # CCI
    tp = (high + low + close) / 3
    ma = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    df['cci'] = (tp - ma) / (0.015 * md + 1e-9)

    # Gold trend (EMA crossover)
    df["gold_trend"] = ((df["ema10"] > df["ema30"]).astype(int) - (df["ema10"] < df["ema30"]).astype(int))

    # Popuni sa 0 ako nema ove kolone
    for col in ['spread', 'volume', 'volatility']:
        if col not in df.columns:
            df[col] = 0

    return df

def generate_trade_features():
    global trade_features_in_progress
    with trade_features_lock:
        if trade_features_in_progress:
            log.warning("⏳ Generisanje trade_features je već u toku! Ignorišem dupli zahtev.")
            return
        trade_features_in_progress = True

        try:
            if not os.path.exists(TRADE_HISTORY_PARQUET):
                log.error(f"❌ Ne postoji istorijski fajl: {TRADE_HISTORY_PARQUET}")
                trade_features_in_progress = False
                return

            df = pd.read_parquet(TRADE_HISTORY_PARQUET)
            if df.empty:
                log.warning("⚠️ Istorijski podaci su prazni.")
                trade_features_in_progress = False
                return

            if "profit" not in df.columns:
                df["profit"] = df["close"].diff().fillna(0) if "close" in df.columns else 0

            df_feat = calculate_indicators(df)

            # Labela 1 ako profit sledećeg reda veći, -1 ako manji, 0 ako isti ili nema sledećeg
            df_feat['label'] = 0
            df_feat.loc[df_feat['profit'].shift(-1) > df_feat['profit'], 'label'] = 1
            df_feat.loc[df_feat['profit'].shift(-1) < df_feat['profit'], 'label'] = -1

            df_feat['trade_id'] = df_feat.index

            columns = [
                "trade_id", "rsi", "macd", "ema10", "ema30", "close", "volume", "spread",
                "adx", "stochastic", "cci", "volatility", "dxy_value", "us30_trend", "spx500_trend",
                "timestamp", "gold_trend", "label"
            ]

            # Popuni obavezne kolone ako fale
            for col in columns:
                if col not in df_feat.columns:
                    if col == "timestamp":
                        df_feat[col] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    elif col in ["dxy_value", "us30_trend", "spx500_trend"]:
                        df_feat[col] = 0
                    else:
                        df_feat[col] = 0

            df_feat = df_feat[columns]

            os.makedirs(os.path.dirname(TRADE_FEATURES_PARQUET), exist_ok=True)
            df_feat.to_parquet(TRADE_FEATURES_PARQUET, index=False)

            log.info(f"✅ trade_features.parquet generisan sa {len(df_feat)} redova.")

        except Exception as e:
            log.error(f"❌ Greška pri generisanju trade_features: {e}")
        finally:
            trade_features_in_progress = False

if __name__ == "__main__":
    generate_trade_features()
