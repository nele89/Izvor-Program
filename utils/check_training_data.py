import os
import pandas as pd

PARQUET_PATH = "data/dukascopy/parquet_resampled/XAUUSD_M1.parquet"  # Prilagodi po potrebi!

def check_training_data():
    if not os.path.exists(PARQUET_PATH):
        print("⚠️ Parquet fajl ne postoji:", PARQUET_PATH)
        return

    df = pd.read_parquet(PARQUET_PATH)
    print(f"🗂 Kolone u fajlu: {list(df.columns)}")

    # Provera redova koji zadovoljavaju AI uslove (primer: volume > 0, volatility <= 15, label -1 ili 1)
    conditions = (df.get("volume", 0) > 0) & (df.get("volatility", 99) <= 15)
    if "label" in df.columns:
        conditions = conditions & (df["label"].isin([-1, 1]))
        valid = df[conditions]
        print(f"📊 Broj zapisa dostupnih za AI trening: {len(valid)}")
        print(f"label value counts:\n{valid['label'].value_counts()}")
    else:
        print("⚠️ Nema 'label' kolone za proveru validnih zapisa.")

    # Prvih nekoliko redova za proveru
    print("\n🔎 Prvih 5 redova:\n", df.head())

if __name__ == "__main__":
    check_training_data()
