import os
import pandas as pd
from datetime import datetime
from logs.logger import log

# Lokacije za fajlove
TRADE_FEATURES_PARQUET = os.path.join("data", "dukascopy", "trade_features.parquet")
TRADE_HISTORY_PARQUET = os.path.join("data", "dukascopy", "trade_history.parquet")
DECISION_MEMORY_PARQUET = os.path.join("data", "dukascopy", "decision_memory.parquet")

def ensure_parquet_file(path, columns=None):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns or [])
        df.to_parquet(path, index=False)
    else:
        df = pd.read_parquet(path)
        if columns:
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            df.to_parquet(path, index=False)

def safe_append(df, row):
    new_df = pd.DataFrame([row])
    new_df = new_df.dropna(axis=1, how='all')
    if new_df.empty or new_df.dropna(how='all').empty:
        return df
    return pd.concat([df, new_df], ignore_index=True)

def get_training_data():
    try:
        columns = [
            "trade_id", "rsi", "macd", "ema10", "ema30", "close", "volume", "spread",
            "adx", "stochastic", "cci", "volatility", "dxy_value", "us30_trend", "spx500_trend",
            "timestamp", "gold_trend", "label"
        ]
        ensure_parquet_file(TRADE_FEATURES_PARQUET, columns=columns)
        df = pd.read_parquet(TRADE_FEATURES_PARQUET)
        return df
    except Exception as e:
        log.error(f"❌ Greška pri dohvatu trening podataka: {e}")
        return pd.DataFrame()

def insert_trade_features(
    trade_id, rsi, macd, ema10, ema30, close, volume, spread,
    adx, stochastic, cci, volatility, dxy_value=None,
    us30_trend=None, spx500_trend=None, timestamp=None, gold_trend=None, label=None
):
    try:
        columns = [
            "trade_id", "rsi", "macd", "ema10", "ema30", "close", "volume", "spread",
            "adx", "stochastic", "cci", "volatility", "dxy_value", "us30_trend", "spx500_trend",
            "timestamp", "gold_trend", "label"
        ]
        ensure_parquet_file(TRADE_FEATURES_PARQUET, columns=columns)
        df = pd.read_parquet(TRADE_FEATURES_PARQUET)
        df = df[df['trade_id'] != trade_id]

        if gold_trend is None:
            if ema10 is not None and ema30 is not None:
                gold_trend = 1 if ema10 > ema30 else -1 if ema10 < ema30 else 0
            else:
                gold_trend = 0

        row = {
            "trade_id": trade_id,
            "rsi": rsi,
            "macd": macd,
            "ema10": ema10,
            "ema30": ema30,
            "close": close,
            "volume": volume,
            "spread": spread,
            "adx": adx,
            "stochastic": stochastic,
            "cci": cci,
            "volatility": volatility,
            "dxy_value": dxy_value,
            "us30_trend": us30_trend,
            "spx500_trend": spx500_trend,
            "timestamp": timestamp or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "gold_trend": gold_trend,
            "label": label
        }
        df = safe_append(df, row)
        df.to_parquet(TRADE_FEATURES_PARQUET, index=False)
        log.info(f"✅ Trade feature sačuvan: {trade_id} | gold_trend={gold_trend}")

    except Exception as e:
        log.error(f"❌ Greška insert_trade_features: {e}")

def get_statistics_by_symbol():
    try:
        ensure_parquet_file(TRADE_HISTORY_PARQUET, columns=["symbol", "profit"])
        df = pd.read_parquet(TRADE_HISTORY_PARQUET)
        if df.empty or "symbol" not in df.columns:
            return []
        result = df.groupby("symbol").agg(
            total_trades=("symbol", "count"),
            total_profit=("profit", "sum"),
            avg_profit=("profit", "mean"),
            max_profit=("profit", "max"),
            min_profit=("profit", "min"),
        ).reset_index()
        return result.to_dict("records")
    except Exception as e:
        log.error(f"❌ Greška u get_statistics_by_symbol: {e}")
        return []

def get_total_trade_count(symbol=None):
    try:
        ensure_parquet_file(TRADE_HISTORY_PARQUET, columns=["symbol"])
        df = pd.read_parquet(TRADE_HISTORY_PARQUET)
        if symbol:
            return len(df[df["symbol"] == symbol])
        return len(df)
    except Exception as e:
        log.error(f"❌ Greška u get_total_trade_count: {e}")
        return 0

def insert_decision(symbol, decision, explanation, result):
    try:
        columns = ["timestamp", "symbol", "decision", "explanation", "result"]
        ensure_parquet_file(DECISION_MEMORY_PARQUET, columns=columns)
        df = pd.read_parquet(DECISION_MEMORY_PARQUET)
        row = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "decision": decision,
            "explanation": explanation,
            "result": result
        }
        df = safe_append(df, row)
        df.to_parquet(DECISION_MEMORY_PARQUET, index=False)
        log.info(f"✅ Decision zapisan: {symbol} → {decision}")
    except Exception as e:
        log.error(f"❌ Greška insert_decision: {e}")

def get_all_decisions():
    try:
        ensure_parquet_file(DECISION_MEMORY_PARQUET, columns=["timestamp", "symbol", "decision", "explanation", "result"])
        df = pd.read_parquet(DECISION_MEMORY_PARQUET)
        return df.to_dict("records")
    except Exception as e:
        log.error(f"❌ Greška u get_all_decisions: {e}")
        return []

def insert_trade_history(
    symbol, entry_time, exit_time, position_type, entry_price, exit_price,
    stop_loss, take_profit, profit, duration, opened_by, outcome,
    is_simulation=0, decision=None, indicators=None
):
    try:
        columns = [
            "symbol", "entry_time", "exit_time", "position_type", "entry_price",
            "exit_price", "stop_loss", "take_profit", "profit", "duration",
            "opened_by", "outcome", "is_simulation", "decision", "indicators"
        ]
        ensure_parquet_file(TRADE_HISTORY_PARQUET, columns=columns)
        df = pd.read_parquet(TRADE_HISTORY_PARQUET)

        def _dt_str(x):
            if isinstance(x, (datetime, pd.Timestamp)):
                return x.strftime("%Y-%m-%d %H:%M:%S")
            try:
                return pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S")
            except:
                return str(x)

        row = {
            "symbol": symbol,
            "entry_time": _dt_str(entry_time),
            "exit_time": _dt_str(exit_time),
            "position_type": position_type,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "profit": profit,
            "duration": duration,
            "opened_by": opened_by,
            "outcome": outcome,
            "is_simulation": int(is_simulation),
            "decision": decision,
            "indicators": str(indicators) if indicators is not None else None
        }

        df = safe_append(df, row)
        for col in ["entry_time", "exit_time"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        df.to_parquet(TRADE_HISTORY_PARQUET, index=False)
        log.info(f"✅ Trade sačuvan za {symbol} @ {row['entry_time']}")

    except Exception as e:
        log.error(f"❌ Greška insert_trade_history: {e}")

def insert_simulated_trade(
    symbol,
    decision,
    indicators,
    entry_time=None,
    exit_time=None,
    entry_price=None,
    exit_price=None,
    profit=None,
    duration=None,
    opened_by="simulator",
    outcome="simulated"
):
    now = entry_time or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    insert_trade_history(
        symbol=symbol,
        entry_time=now,
        exit_time=exit_time or now,
        position_type="sim",
        entry_price=entry_price,
        exit_price=exit_price,
        stop_loss=None,
        take_profit=None,
        profit=profit,
        duration=duration,
        opened_by=opened_by,
        outcome=outcome,
        is_simulation=1,
        decision=decision,
        indicators=indicators
    )

def get_trades_in_period(start_date, end_date, symbol=None):
    try:
        ensure_parquet_file(TRADE_HISTORY_PARQUET, columns=["symbol", "entry_time"])
        df = pd.read_parquet(TRADE_HISTORY_PARQUET)
        df["entry_time"] = pd.to_datetime(df["entry_time"])
        mask = (df["entry_time"] >= pd.to_datetime(start_date)) & (df["entry_time"] <= pd.to_datetime(end_date))
        if symbol:
            mask &= (df["symbol"] == symbol)
        return df[mask]
    except Exception as e:
        log.error(f"❌ Greška u get_trades_in_period: {e}")
        return pd.DataFrame()
