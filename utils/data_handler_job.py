import os
import pandas as pd
from logs.logger import log

def data_handler_job(
    input_dir="data/converted",
    output_dir="data/processed",
    timeframes=None,
    symbol="XAUUSD"
):
    if timeframes is None:
        timeframes = ["M1", "M5", "H1"]

    os.makedirs(output_dir, exist_ok=True)

    for tf in timeframes:
        fname = f"{symbol}_{tf}.csv"
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)

        if not os.path.exists(in_path):
            log.warning(f"[DATA HANDLER] Fajl ne postoji: {in_path}")
            continue

        try:
            df = pd.read_csv(in_path)
            # Čišćenje podataka
            df = clean_data(df)
            # Kreiranje dodatnih feature-a
            df = feature_engineering(df)

            df.to_csv(out_path, index=False)
            log.info(f"[DATA HANDLER] Obrada završena za {fname} ({len(df)} redova)")

        except Exception as e:
            log.error(f"[DATA HANDLER] Greška za {fname}: {e}")

def clean_data(df):
    # Ukloni redove koji imaju bilo koju NaN vrednost
    df = df.dropna()
    # Ovde možeš dodati dodatna pravila za čišćenje po potrebi
    return df

def feature_engineering(df):
    # Dodavanje 'mid' kolone kao srednje vrednosti bid i ask ako postoje
    if "bid" in df.columns and "ask" in df.columns:
        df["mid"] = (df["bid"] + df["ask"]) / 2
    # Dodaj dodatne feature-e po potrebi
    return df

if __name__ == "__main__":
    data_handler_job()
