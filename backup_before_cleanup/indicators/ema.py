def calculate_ema(series, period=20):
    """Računa Exponential Moving Average (EMA)."""
    return series.ewm(span=period, adjust=False).mean()
