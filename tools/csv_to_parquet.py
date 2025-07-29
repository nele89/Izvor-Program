import os
import pandas as pd
import json
import shutil
from logs.logger import log  # koristi tvoj logger sistem

CSV_FOLDER = os.path.join("data", "dukascopy", "XAUUSD")
PARQUET_FILE = os.path.join("data", "dukascopy", "trade_history.parquet")
CONVERT_LOG = os.path.join("data", "dukascopy", "convert_log.json")

REQUIRED_COLUMNS = ["time", "bid", "ask", "volume"]  # spread se računa ako ga nema

def load_convert_log():
    if os.path.exists(CONVERT_LOG):
        try:
            with open(CONVERT_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_convert_log(log_data):
    try:
        if os.path.exists(CONVERT_LOG):
            shutil.copy2(CONVERT_LOG, CONVERT_LOG + ".bak")
        with open(CONVERT_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as ex:
        log.warning(f"❌ Ne mogu da upišem convert_log: {ex}")

def csv_folder_to_parquet(csv_folder=CSV_FOLDER, parquet_file=PARQUET_FILE):
    all_dfs = []
    convert_log = load_convert_log()
    updated_log = {}

    for f in os.listdir(csv_folder):
        if f.endswith('.csv'):
            file_path = os.path.join(csv_folder, f)
            try:
                df = pd.read_csv(file_path)

                # Provera da li postoje sve obavezne kolone
                if not all(col in df.columns for col in REQUIRED_COLUMNS):
                    log.warning(f"⚠️ Preskačem fajl (nedostaju obavezne kolone): {file_path}")
                    continue

                # Pretvori kolonu time u datetime
                df["time"] = pd.to_datetime(df["time"], errors="coerce")
                df = df.dropna(subset=["time"])

                # Ako nema spread kolonu – izračunaj je
                if "spread" not in df.columns:
                    df["spread"] = df["ask"] - df["bid"]

                all_dfs.append(df)
                updated_log[f] = {
                    "csv_mtime": int(os.path.getmtime(file_path)),
                    "rows": len(df),
                }

            except Exception as e:
                log.error(f"❌ Greška pri čitanju fajla {file_path}: {e}")

    if not all_dfs:
        log.warning("⚠️ Nema validnih CSV fajlova za obradu.")
        return

    # Kombinuj i sortiraj
    big_df = pd.concat(all_dfs, ignore_index=True)
    big_df = big_df.sort_values("time")
    big_df.to_parquet(parquet_file, index=False)

    log.info(f"✅ Upisano {len(big_df)} redova u {parquet_file}")

    updated_log["master_parquet"] = {
        "filename": os.path.basename(parquet_file),
        "rows": len(big_df),
        "size": os.path.getsize(parquet_file),
        "mtime": int(os.path.getmtime(parquet_file))
    }
    save_convert_log(updated_log)

if __name__ == "__main__":
    csv_folder_to_parquet()
