import numpy as np
import pandas as pd

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Provera osnovnih kolona
    required_cols = ["close", "high", "low"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"❌ Nedostaje kolona: {col}")

    # EMA indikatori
    df["ema10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["ema30"] = df["close"].ewm(span=30, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / (roll_down + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    # CCI
    tp = (df["high"] + df["low"] + df["close"]) / 3
    ma = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df["cci"] = (tp - ma) / (0.015 * md + 1e-9)

    # Stochastic Oscillator
    low_min = df["low"].rolling(14).min()
    high_max = df["high"].rolling(14).max()
    df["stochastic"] = 100 * ((df["close"] - low_min) / (high_max - low_min + 1e-9))

    # ADX
    plus_dm = df["high"].diff().clip(lower=0)
    minus_dm = -df["low"].diff().clip(upper=0)
    tr1 = (df["high"] - df["low"]).abs()
    tr2 = (df["high"] - df["close"].shift()).abs()
    tr3 = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / (atr + 1e-9))
    minus_di = 100 * (minus_dm.rolling(14).mean() / (atr + 1e-9))
    df["adx"] = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)).rolling(14).mean()

    # Gold trend (logička relacija)
    df["gold_trend"] = ((df["ema10"] > df["ema30"]).astype(int) -
                        (df["ema10"] < df["ema30"]).astype(int))

    # Ako nedostaju kolone volume i spread, popuni nulama
    for col in ["volume", "spread"]:
        if col not in df.columns:
            df[col] = 0

    return df
