# indicators/indicator_utils.py

import pandas as pd
import numpy as np

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)

def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line.fillna(0), signal_line.fillna(0), histogram.fillna(0)

def calculate_ma(df, period):
    return df['close'].rolling(window=period).mean().fillna(0)

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr.fillna(0)

def calculate_supertrend(df, period=10, multiplier=3):
    atr = calculate_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()
    supertrend = [1] * len(df)  # 1 = bullish, 0 = bearish

    for i in range(1, len(df)):
        if df['close'][i] > final_upperband[i - 1]:
            supertrend[i] = 1
        elif df['close'][i] < final_lowerband[i - 1]:
            supertrend[i] = 0
        else:
            supertrend[i] = supertrend[i - 1]

            if supertrend[i] == 1 and lowerband[i] > final_lowerband[i - 1]:
                final_lowerband[i] = final_lowerband[i - 1]

            if supertrend[i] == 0 and upperband[i] < final_upperband[i - 1]:
                final_upperband[i] = final_upperband[i - 1]

    return pd.Series(supertrend, index=df.index)

def calculate_all_indicators(df, indicator_list):
    result = df.copy()

    if "RSI" in indicator_list:
        result["RSI"] = calculate_rsi(result)

    if "MACD" in indicator_list:
        macd_line, signal_line, hist = calculate_macd(result)
        result["MACD_Line"] = macd_line
        result["MACD_Signal"] = signal_line
        result["MACD_Hist"] = hist

    if "MA50" in indicator_list:
        result["MA50"] = calculate_ma(result, 50)

    if "MA200" in indicator_list:
        result["MA200"] = calculate_ma(result, 200)

    if "ATR" in indicator_list:
        result["ATR"] = calculate_atr(result)

    if "Supertrend" in indicator_list:
        result["Supertrend"] = calculate_supertrend(result)

    # Budući indikatori:
    # if "EMA20" in indicator_list:
    #     result["EMA20"] = df['close'].ewm(span=20).mean().fillna(0)

    return result
