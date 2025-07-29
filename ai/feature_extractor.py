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

def extract_features(data_row):
    # Ako je pandas.Series, konvertuj u dict
    if hasattr(data_row, "to_dict"):
        data_row = data_row.to_dict()

    features = {}
    # Prvo pokupi sve standardne feature-e (osim gold_trend)
    for feat in FEATURE_ORDER:
        if feat != "gold_trend":
            features[feat] = data_row.get(feat, 0)

    # Logika za gold_trend ako ga nema
    if "gold_trend" in data_row and data_row["gold_trend"] != 0:
        features["gold_trend"] = data_row["gold_trend"]
    elif "ema10" in features and "ema30" in features:
        if features["ema10"] > features["ema30"]:
            features["gold_trend"] = 1
        elif features["ema10"] < features["ema30"]:
            features["gold_trend"] = -1
        else:
            features["gold_trend"] = 0
    else:
        features["gold_trend"] = 0

    return features

# Primer upotrebe:
if __name__ == "__main__":
    row = {
        "rsi": 50,
        "macd": 0.2,
        "ema10": 18000000,
        "ema30": 12000000,
        "close": 2100000,
        "volume": 6e10,
        "spread": 0,
        "adx": 20,
        "stochastic": 70,
        "cci": 100
        # gold_trend nije naveden, BIĆE AUTOMA**TSKI** IZRACUNAT
    }
    print(extract_features(row))
