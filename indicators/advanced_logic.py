# indicators/advanced_logic.py

import numpy as np
import pandas as pd

def detect_golden_cross(df):
    if "MA50" not in df or "MA200" not in df:
        return False
    if df["MA50"].iloc[-2] < df["MA200"].iloc[-2] and df["MA50"].iloc[-1] > df["MA200"].iloc[-1]:
        return True
    return False

def detect_death_cross(df):
    if "MA50" not in df or "MA200" not in df:
        return False
    if df["MA50"].iloc[-2] > df["MA200"].iloc[-2] and df["MA50"].iloc[-1] < df["MA200"].iloc[-1]:
        return True
    return False

def detect_rsi_divergence(df, threshold=10):
    if "RSI" not in df or len(df) < 3:
        return False
    delta = df["RSI"].diff()
    return (delta.iloc[-1] < -threshold) or (delta.iloc[-1] > threshold)

def calculate_signal_score(df):
    """Kombinuje više indikatora i vraća skor između 0 i 100"""
    score = 0
    total = 0

    # RSI signal
    if "RSI" in df.columns:
        rsi = df["RSI"].iloc[-1]
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1
        total += 1

    # MACD histogram signal
    if "MACD_Hist" in df.columns:
        hist = df["MACD_Hist"].iloc[-1]
        if hist > 0:
            score += 1
        else:
            score -= 1
        total += 1

    # Supertrend
    if "Supertrend" in df.columns:
        trend = df["Supertrend"].iloc[-1]
        if trend:
            score += 1
        else:
            score -= 1
        total += 1

    # MA trend
    if "MA50" in df.columns and "MA200" in df.columns:
        if df["MA50"].iloc[-1] > df["MA200"].iloc[-1]:
            score += 1
        else:
            score -= 1
        total += 1

    if total == 0:
        return 50  # neutral
    normalized = 50 + (score / total) * 50  # skala 0–100
    return round(normalized, 2)

def evaluate_advanced_signals(df):
    return {
        "golden_cross": detect_golden_cross(df),
        "death_cross": detect_death_cross(df),
        "rsi_divergence": detect_rsi_divergence(df),
        "signal_score": calculate_signal_score(df)
    }
