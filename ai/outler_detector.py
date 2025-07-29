# 📁 ai/outlier_detector.py

import pandas as pd
import os
from logs.logger import log

PARQUET_PATH = os.path.join("data", "dukascopy", "parquet_resampled", "XAUUSD_M1.parquet")

def load_data_for_outlier_check():
    """Učitaj sve trejdove i njihove indikatore iz Parquet fajla."""
    if not os.path.exists(PARQUET_PATH):
        log.warning(f"⚠️ Parquet fajl ne postoji za analizu outliera: {PARQUET_PATH}")
        return pd.DataFrame()
    try:
        df = pd.read_parquet(PARQUET_PATH)
        # Samo relevantne kolone za analizu
        columns = [
            "rsi", "macd", "ema10", "ema30", "close", "volume",
            "spread", "adx", "stochastic", "cci", "gold_trend"
        ]
        cols = [col for col in columns if col in df.columns]
        df = df[cols]
        df.dropna(inplace=True)
        return df
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju Parquet za outlier proveru: {e}")
        return pd.DataFrame()

def detect_outliers_iqr(df: pd.DataFrame):
    """
    Detekcija outliera po IQR metodi za sve numeričke kolone.
    Vraća rečnik sa nazivom kolone i brojem otkrivenih outliera.
    """
    outlier_summary = {}

    for column in df.columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[column] < lower) | (df[column] > upper)]
        outlier_count = outliers.shape[0]

        if outlier_count > 0:
            outlier_summary[column] = outlier_count

    return outlier_summary

def run_outlier_check():
    df = load_data_for_outlier_check()
    if df.empty:
        log.warning("⚠️ Nema podataka za outlier proveru.")
        return

    summary = detect_outliers_iqr(df)

    if not summary:
        log.info("✅ Nisu pronađeni statistički outlieri u podacima.")
    else:
        log.warning("🚨 Otkriveni outlieri po indikatorima:")
        for column, count in summary.items():
            log.warning(f"🔹 {column}: {count} outliera")

if __name__ == "__main__":
    run_outlier_check()
