import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from logs.logger import log

# Glavna funkcija za signal

def get_trade_signal(symbol, timeframe=mt5.TIMEFRAME_M5, settings=None):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    if rates is None or len(rates) == 0:
        log.warning(f"Nema podataka za simbol {symbol}")
        return None

    df = pd.DataFrame(rates)
    df['close'] = df['close'].astype(float)

    # AI logika moze biti ovde kasnije
    short_ma = df['close'].rolling(window=5).mean()
    long_ma = df['close'].rolling(window=20).mean()

    if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
        return "buy"
    elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
        return "sell"
    return None


def calculate_tp_sl(symbol, signal, strategy="dynamic", percentage=1.5, atr_period=14, atr_multiplier=2.0):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
    if rates is None or len(rates) == 0:
        log.warning(f"Nema dostupnih podataka za {symbol}")
        return (0, 0)

    df = pd.DataFrame(rates)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    last_price = df['close'].iloc[-1]

    if strategy == "dynamic":
        recent_high = df['high'].iloc[-5:].max()
        recent_low = df['low'].iloc[-5:].min()
        tp = abs(recent_high - recent_low)
        sl = tp / 2

    elif strategy == "percentage":
        tp = last_price * (percentage / 100)
        sl = tp / 1.5

    elif strategy == "volatility_based":
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(abs(df['high'] - df['close'].shift()), abs(df['low'] - df['close'].shift()))
        )
        df['atr'] = df['tr'].rolling(window=atr_period).mean()
        atr = df['atr'].iloc[-1]
        tp = atr * atr_multiplier
        sl = atr * (atr_multiplier / 1.5)

    else:
        log.warning(f"Nepoznata TP/SL strategija: {strategy}")
        return (0, 0)

    log.info(f"TP/SL ({strategy}) za {symbol}: TP={tp:.2f}, SL={sl:.2f}")
    return (tp, sl)
