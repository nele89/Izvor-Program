import os
import pandas as pd
import json
import shutil
import threading
from tqdm import tqdm
from logs.logger import log

# Mesto gde su skriveni mali Parquet fajlovi
PARQUET_RAW_DIR = os.path.join("data", "dukascopy", "parquet_raw")
# Putanja za izlazni veliki Parquet
OUT_PATH = os.path.join("data", "dukascopy", "trade_history.parquet")
MERGE_LOG = os.path.join("data", "dukascopy", "merge_log.json")

# Globalni lock i flag
merge_lock = threading.Lock()
merge_in_progress = False

# Učitaj i sačuvaj log o merge-u

def load_merge_log():
    if os.path.exists(MERGE_LOG):
        try:
            with open(MERGE_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"⚠️ Greška pri učitavanju merge_log: {e}")
    return {}

def save_merge_log(log_data):
    try:
        if os.path.exists(MERGE_LOG):
            shutil.copy2(MERGE_LOG, MERGE_LOG + ".bak")
        with open(MERGE_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as ex:
        log.warning(f"❌ Ne mogu da upišem merge_log: {ex}")

# Glavna funkcija za merge Parquet fajlova

def merge_all_parquet():
    global merge_in_progress
    with merge_lock:
        if merge_in_progress:
            log.warning("⏳ Merge Parquet fajlova je već u toku! Ignorišem dupli zahtev.")
            return
        merge_in_progress = True

        if not os.path.isdir(PARQUET_RAW_DIR):
            log.error(f"❌ Folder sa malim Parquet fajlovima ne postoji: {PARQUET_RAW_DIR}")
            merge_in_progress = False
            return

        pq_files = [f for f in os.listdir(PARQUET_RAW_DIR) if f.endswith('.parquet')]
        if not pq_files:
            log.warning(f"⚠️ Nema Parquet fajlova za spajanje u {PARQUET_RAW_DIR}")
            merge_in_progress = False
            return

        all_dfs = []
        for fname in tqdm(sorted(pq_files), desc="Merging Parquets", unit="file"):
            fpath = os.path.join(PARQUET_RAW_DIR, fname)
            try:
                df = pd.read_parquet(fpath)
                all_dfs.append(df)
            except Exception as e:
                log.error(f"❌ Greška prilikom čitanja {fname}: {e}")

        if not all_dfs:
            log.warning("⚠️ Nema validnih podataka za spajanje.")
            merge_in_progress = False
            return

        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_df = merged_df.sort_values('time').drop_duplicates(subset='time').reset_index(drop=True)

        if os.path.exists(OUT_PATH):
            shutil.copy2(OUT_PATH, OUT_PATH + '.bak')
            log.info("🗂️ Backup postojećeg trade_history.parquet napravljen.")

        merged_df.to_parquet(OUT_PATH, index=False)
        log.info(f"✅ Spojen i sačuvan trade_history.parquet sa {len(merged_df)} redova.")

        merge_log = {
            'files_merged': len(pq_files),
            'rows_total': len(merged_df),
            'last_updated': pd.Timestamp.now().isoformat()
        }
        save_merge_log(merge_log)
        merge_in_progress = False

if __name__ == '__main__':
    merge_all_parquet()
