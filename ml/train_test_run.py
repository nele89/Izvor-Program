import pandas as pd
from model_trainer import train_model

# ✅ Test podaci sa indikatorima (dummy vrednosti)
data = {
    "close": [100, 102, 101, 103, 104, 102, 101, 105, 107, 106],
    "rsi": [50, 52, 51, 53, 55, 50, 48, 60, 62, 59],
    "macd": [0.5, 0.6, 0.4, 0.7, 0.8, 0.3, 0.2, 0.9, 1.0, 0.8],
    "macd_signal": [0.4, 0.5, 0.4, 0.6, 0.7, 0.3, 0.2, 0.85, 0.95, 0.75],
    "%K": [30, 40, 35, 45, 50, 25, 20, 55, 60, 58],
    "%D": [32, 38, 36, 42, 48, 28, 22, 52, 58, 55],
    "tenkan_sen": [101, 102, 101, 103, 104, 102, 100, 105, 107, 106],
    "kijun_sen": [100, 101, 100, 102, 103, 101, 99, 104, 106, 105],
    "adx": [20, 22, 21, 23, 25, 19, 18, 27, 28, 26]
}

df = pd.DataFrame(data)

# 🧠 Poziv treniranja modela
train_model(df)
