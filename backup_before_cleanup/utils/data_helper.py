import os
import pandas as pd

DATA_DIR = os.path.join("data", "dukascopy", "parquet_resampled")
TRADE_FILE = os.path.join(DATA_DIR, "trades.parquet")      # fajl za evidenciju svih trejdova
DECISION_FILE = os.path.join(DATA_DIR, "decisions.parquet")  # fajl za evidenciju odluka AI
M1_FILE = os.path.join(DATA_DIR, "XAUUSD_M1.parquet")      # M1 parquet podaci za trening

def _safe_read_parquet(path):
    """Sigurno učitava parquet fajl ako postoji, inače vraća prazan DataFrame."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    else:
        return pd.DataFrame()

def _safe_write_parquet(df, path):
    """Sigurno upisuje DataFrame u parquet fajl, kreira folder ako ne postoji."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)

def get_all_trades():
    """Vraća sve trejdove iz fajla trades.parquet."""
    return _safe_read_parquet(TRADE_FILE)

def get_total_trade_count(symbol=None):
    """Vraća ukupan broj trejdova, ili po simbolu ako je prosleđen."""
    df = get_all_trades()
    if symbol is not None:
        return len(df[df['symbol'] == symbol])
    return len(df)

def get_statistics_by_symbol():
    """Vraća listu statistika (ukupan profit, broj trejdova itd.) po simbolu."""
    df = get_all_trades()
    if df.empty:
        return []
    result = []
    for symbol, group in df.groupby('symbol'):
        result.append({
            "symbol": symbol,
            "total_trades": len(group),
            "total_profit": group['profit'].sum(),
            "avg_profit": group['profit'].mean(),
            "max_profit": group['profit'].max(),
            "min_profit": group['profit'].min()
        })
    return result

def insert_trade(trade_dict):
    """Dodaje jedan novi trejd u fajl trades.parquet."""
    df = get_all_trades()
    new_df = pd.DataFrame([trade_dict])
    df = pd.concat([df, new_df], ignore_index=True)
    _safe_write_parquet(df, TRADE_FILE)

def insert_decision(symbol, decision, explanation, result):
    """Dodaje novu AI odluku u fajl decisions.parquet."""
    df = _safe_read_parquet(DECISION_FILE)
    new_row = {
        "timestamp": pd.Timestamp.now(),
        "symbol": symbol,
        "decision": decision,
        "explanation": explanation,
        "result": result
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _safe_write_parquet(df, DECISION_FILE)

def get_training_data(tf="M1"):
    """Vraća podatke za trening sa parquet fajla za dati timeframe (default 'M1')."""
    file_map = {
        "M1": os.path.join(DATA_DIR, "XAUUSD_M1.parquet"),
        "M5": os.path.join(DATA_DIR, "XAUUSD_M5.parquet"),
        "H1": os.path.join(DATA_DIR, "XAUUSD_H1.parquet"),
    }
    return _safe_read_parquet(file_map.get(tf, M1_FILE))

def clear_all_trades():
    """Briše ceo fajl sa trejdovima (koristiti pažljivo)."""
    if os.path.exists(TRADE_FILE):
        os.remove(TRADE_FILE)

def clear_all_decisions():
    """Briše ceo fajl sa AI odlukama (koristiti pažljivo)."""
    if os.path.exists(DECISION_FILE):
        os.remove(DECISION_FILE)
