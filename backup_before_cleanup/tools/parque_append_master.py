import os
import pandas as pd
from glob import glob

CSV_DIR = os.path.join("data", "dukascopy", "XAUUSD")
PARQUET_FILE = os.path.join("data", "dukascopy", "trade_history.parquet")

def append_csvs_to_parquet():
    # Prikupi sve CSV fajlove
    csv_files = sorted(set(glob(os.path.join(CSV_DIR, "*.csv"))))  # osiguravaš da nema duplikata
    if not csv_files:
        print("⚠️ Nema CSV fajlova za obradu.")
        return

    # Ako već postoji Parquet, učitaj postojeće podatke
    if os.path.exists(PARQUET_FILE):
        master = pd.read_parquet(PARQUET_FILE)
        existing_times = set(pd.to_datetime(master["time"]).astype("datetime64[ns]"))
        print(f"📦 Učitano već postojećih redova: {len(master)}")
    else:
        master = pd.DataFrame()
        existing_times = set()
        print("📦 Kreiram novi Parquet.")

    total_new = 0
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "time" not in df.columns:
                print(f"⚠️ Preskačem {file} (nema 'time' kolonu)")
                continue
            df["time"] = pd.to_datetime(df["time"]).astype("datetime64[ns]")
            # Dodaj samo nove redove
            df = df[~df["time"].isin(existing_times)].copy()
            if not df.empty:
                master = pd.concat([master, df], ignore_index=True)
                existing_times.update(df["time"])
                print(f"✅ Dodato {len(df)} redova iz {os.path.basename(file)}")
                total_new += len(df)
        except Exception as e:
            print(f"❌ Greška sa {file}: {e}")

    if not master.empty:
        # Sortiraj po vremenu
        master = master.sort_values("time").reset_index(drop=True)
        master.to_parquet(PARQUET_FILE, index=False)
        print(f"🎉 Parquet ažuriran: {PARQUET_FILE} ({len(master)} redova, novih: {total_new})")
    else:
        print("⚠️ Nema novih podataka za dodavanje.")

if __name__ == "__main__":
    append_csvs_to_parquet()
