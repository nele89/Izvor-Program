import os
import pandas as pd
from logs.logger import log  # Ako koristiš logger, ili možeš da izbaciš

def rebuild_master_parquet():
    input_folder = os.path.join("data", "dukascopy", "parquet_raw")
    output_file = os.path.join("data", "dukascopy", "master.parquet")

    if not os.path.exists(input_folder):
        print(f"❌ Ulazni folder ne postoji: {input_folder}")
        return

    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".parquet")]
    if not files:
        print("⚠️ Nema parquet fajlova za spajanje.")
        return

    dfs = []
    for fpath in files:
        try:
            df = pd.read_parquet(fpath)
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ Greška pri čitanju {fpath}: {e}")

    if not dfs:
        print("⚠️ Nema uspešno učitanih fajlova.")
        return

    master_df = pd.concat(dfs, ignore_index=True)
    master_df.to_parquet(output_file, index=False)
    print(f"✅ Spojeno {len(files)} fajlova u '{output_file}' sa ukupno {len(master_df)} redova.")

if __name__ == "__main__":
    rebuild_master_parquet()
