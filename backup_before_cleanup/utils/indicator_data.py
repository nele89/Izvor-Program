import MetaTrader5 as mt5
import pandas as pd

def get_live_indicators(symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M5):
    print("[DEBUG] get_live_indicators POZVAN")

    if not mt5.initialize():
        print("[DEBUG] MT5 init fail")
        return None

    try:
        # Povuci 200 sveća (za EMA, RSI, itd.)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
        df = pd.DataFrame(rates)
        if df.empty or len(df) < 50:
            print("[DEBUG] Nema dovoljno podataka za indikatore.")
            return None

        # RSI
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12.iloc[-1] - ema26.iloc[-1]

        # EMA10 i EMA30
        ema10 = df['close'].ewm(span=10, adjust=False).mean().iloc[-1]
        ema30 = df['close'].ewm(span=30, adjust=False).mean().iloc[-1]

        # Close cena i volume
        close = df['close'].iloc[-1]
        volume = float(df['real_volume'].iloc[-1])

        # Spread (na osnovu tick info)
        tick = mt5.symbol_info_tick(symbol)
        spread = tick.ask - tick.bid if tick else 0.0

        # Volatilnost (razlika max-high i min-low za poslednjih 14 sveća)
        volatility = df['high'].rolling(window=14).max().iloc[-1] - df['low'].rolling(window=14).min().iloc[-1]

        # Dummy vrednosti za ostale indikatore (dodaj kasnije pravu logiku)
        adx = 25.0
        stochastic = 55.0
        cci = 100.0

        # GOLD_TREND LOGIKA
        if ema10 > ema30:
            gold_trend = 1
        elif ema10 < ema30:
            gold_trend = -1
        else:
            gold_trend = 0

        result = {
            "rsi": round(rsi.iloc[-1], 2),
            "macd": round(macd, 5),
            "ema10": round(ema10, 5),
            "ema30": round(ema30, 5),
            "close": round(close, 5),
            "volume": volume,
            "spread": round(spread, 5),
            "adx": adx,
            "stochastic": stochastic,
            "cci": cci,
            "gold_trend": gold_trend
        }

        print("[DEBUG] get_live_indicators VRACA:", result)
        return result

    except Exception as e:
        print(f"Greška u get_live_indicators: {e}")
        return None
    finally:
        mt5.shutdown()
