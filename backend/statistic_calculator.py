import os
import pandas as pd
from logs.logger import log
from utils.db_manager import get_trades_in_period

def calculate_statistics(start_date, end_date, symbol=None):
    """Izračunava osnovne i napredne statistike trejdova za zadati period i simbol."""
    trades = get_trades_in_period(start_date, end_date, symbol)
    if not trades or len(trades) == 0:
        log.warning("⚠️ Nema podataka za izračun statistike.")
        return {}

    columns = [
        "id", "symbol", "entry_time", "exit_time", "position_type", "entry_price",
        "exit_price", "stop_loss", "take_profit", "profit", "duration", "opened_by", "outcome"
    ]
    df = pd.DataFrame(trades, columns=columns)

    stats = {}

    stats["total_trades"] = len(df)
    stats["total_profit"] = df["profit"].sum()
    stats["average_profit"] = df["profit"].mean()
    stats["max_profit"] = df["profit"].max()
    stats["min_profit"] = df["profit"].min()
    stats["win_rate"] = (df["profit"] > 0).mean() * 100
    stats["loss_rate"] = (df["profit"] < 0).mean() * 100
    stats["average_win"] = df[df["profit"] > 0]["profit"].mean() if (df["profit"] > 0).any() else 0.0
    stats["average_loss"] = df[df["profit"] < 0]["profit"].mean() if (df["profit"] < 0).any() else 0.0
    stats["profit_factor"] = abs(df[df["profit"] > 0]["profit"].sum() / df[df["profit"] < 0]["profit"].sum()) if (df["profit"] < 0).any() else float('inf')
    stats["average_duration"] = df["duration"].mean()
    stats["longest_trade"] = df["duration"].max()
    stats["shortest_trade"] = df["duration"].min()

    # Napredne statistike (možete proširiti po potrebi)
    stats["std_dev_profit"] = df["profit"].std()
    stats["median_profit"] = df["profit"].median()

    return stats
