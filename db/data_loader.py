import pandas as pd

FEATURE_ORDER = [
    "rsi",
    "macd",
    "ema10",
    "ema30",
    "close",
    "volume",
    "spread",
    "adx",
    "stochastic",
    "cci",
    "gold_trend"
]

def load_data_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    for feat in FEATURE_ORDER:
        if feat not in df.columns:
            df[feat] = 0
    df["gold_trend"] = (
        (df["ema10"] > df["ema30"]).astype(int) - (df["ema10"] < df["ema30"]).astype(int)
    )
    features = df[FEATURE_ORDER].copy()
    label = df["label"] if "label" in df.columns else pd.Series([0] * len(df))
    return features, label

def load_data_from_parquet(parquet_path):
    df = pd.read_parquet(parquet_path)
    for feat in FEATURE_ORDER:
        if feat not in df.columns:
            df[feat] = 0
    df["gold_trend"] = (
        (df["ema10"] > df["ema30"]).astype(int) - (df["ema10"] < df["ema30"]).astype(int)
    )
    features = df[FEATURE_ORDER].copy()
    label = df["label"] if "label" in df.columns else pd.Series([0] * len(df))
    return features, label

if __name__ == "__main__":
    # Test iz CSV
    features, label = load_data_from_csv("data/XAUUSD/dataset_ai.csv")
    print(features.head())
    print(label.head())

    # Test iz Parquet
    features_pq, label_pq = load_data_from_parquet("data/dukascopy/parquet_resampled/XAUUSD_M1.parquet")
    print(features_pq.head())
    print(label_pq.head())
