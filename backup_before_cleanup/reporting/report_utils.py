# reporting/report_utils.py

import pandas as pd
from datetime import timedelta

def calculate_basic_statistics(df):
    stats = {}

    stats["total_trades"] = len(df)
    stats["winning_trades"] = len(df[df["outcome"] == "win"])
    stats["losing_trades"] = len(df[df["outcome"] == "loss"])
    stats["win_rate (%)"] = round((stats["winning_trades"] / stats["total_trades"]) * 100, 2) if stats["total_trades"] > 0 else 0
    stats["total_profit"] = round(df["profit"].sum(), 2)
    stats["avg_profit"] = round(df["profit"].mean(), 2) if stats["total_trades"] > 0 else 0
    stats["max_profit"] = round(df["profit"].max(), 2) if stats["total_trades"] > 0 else 0
    stats["max_loss"] = round(df["profit"].min(), 2) if stats["total_trades"] > 0 else 0

    # Trajanje trejdova
    if "duration" in df.columns:
        stats["avg_duration"] = round(df["duration"].mean(), 2)
    else:
        stats["avg_duration"] = "n/a"

    return stats


def filter_by_period(df, period="daily"):
    now = pd.Timestamp.now()

    if period == "daily":
        return df[df["entry_time"].dt.date == now.date()]
    elif period == "weekly":
        return df[df["entry_time"].dt.isocalendar().week == now.isocalendar().week]
    elif period == "monthly":
        return df[df["entry_time"].dt.month == now.month]
    elif period == "yearly":
        return df[df["entry_time"].dt.year == now.year]
    else:
        return df
