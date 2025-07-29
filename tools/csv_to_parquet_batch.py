import os
import pandas as pd
from tqdm import tqdm
import json
import shutil
import threading
from logs.logger import log  # koristi tvoj logger

CSV_DIR = os.path.join("data", "dukascopy", "XAUUSD")
PARQUET_DIR = os.path.join("data", "dukascopy", "parquet_raw")
CONVERT_LOG = os.path.join("data", "dukascopy", "convert_log.json")

os.makedirs(PARQUET_DIR, exist_ok=True)

# Dodaj globalni lock (ili koristi iz glavnog modula ako ga već imaš)
conversion_lock = threading.Lock()
conversion_in_progress = False

def load_convert_log():
    if os.path.exists(CONVERT_LOG):
        try:
            with open(CONVERT_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"⚠️ Greška pri učitavanju convert_log: {e}")
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

def convert_all_csv_to_parquet():
    global conversion_in_progress
    with conversion_lock:
        if conversion_in_progress:
            log.warning("⏳ Konverzija CSV → Parquet je već u toku! Ignorišem dupli zahtev.")
            return
        conversion_in_progress = True

        abs_csv_dir = os.path.abspath(CSV_DIR)
        abs_parquet_dir = os.path.abspath(PARQUET_DIR)

        if not os.path.isdir(CSV_DIR):
            log.error(f"❌ Folder sa CSV fajlovima NE postoji: {abs_csv_dir}")
            conversion_in_progress = False
            return

        csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
        if not csv_files:
            log.warning(f"⚠️ Nema CSV fajlova za konverziju u: {abs_csv_dir}")
            conversion_in_progress = False
            return

        log.info(f"🔎 Pronađeno {len(csv_files)} CSV fajlova za konverziju...")

        converted = 0
        skipped = 0
        convert_log = load_convert_log()

        for csv_file in tqdm(sorted(csv_files), desc="Konvertujem CSV → Parquet", unit="fajl"):
            csv_path = os.path.join(CSV_DIR, csv_file)
            base = os.path.splitext(csv_file)[0]
            pq_path = os.path.join(PARQUET_DIR, base + ".parquet")

            csv_mtime = int(os.path.getmtime(csv_path))
            pq_exists = os.path.exists(pq_path)
            pq_mtime = int(os.path.getmtime(pq_path)) if pq_exists else 0
            prev_entry = convert_log.get(csv_file)

            # Glavna provera: Parquet postoji i NIJE stariji od CSV-a (nezavisno od loga)
            if pq_exists and pq_mtime >= csv_mtime:
                # Provera dodatno i loga za backward kompatibilnost
                if (
                    isinstance(prev_entry, dict)
                    and prev_entry.get("csv_mtime") == csv_mtime
                    and prev_entry.get("pq_mtime") == pq_mtime
                ) or prev_entry == csv_mtime:
                    skipped += 1
                    continue
                else:
                    # Parquet je sveže regenerisan mimo loga - preskoči i sada upiši novi log
                    try:
                        pq_size = os.path.getsize(pq_path)
                        df_rows = pd.read_parquet(pq_path).shape[0]
                    except Exception:
                        pq_size = 0
                        df_rows = 0
                    convert_log[csv_file] = {
                        "csv_mtime": csv_mtime,
                        "rows": df_rows,
                        "pq_size": pq_size,
                        "pq_mtime": pq_mtime,
                    }
                    skipped += 1
                    continue

            try:
                df = pd.read_csv(csv_path)
                df.to_parquet(pq_path, index=False)

                pq_mtime = int(os.path.getmtime(pq_path))
                pq_size = os.path.getsize(pq_path)

                convert_log[csv_file] = {
                    "csv_mtime": csv_mtime,
                    "rows": len(df),
                    "pq_size": pq_size,
                    "pq_mtime": pq_mtime,
                }
                converted += 1

            except Exception as e:
                log.warning(f"⚠️ Greška prilikom konverzije '{csv_file}': {e}")
                skipped += 1

        save_convert_log(convert_log)

        log.info(f"✅ Konverzija završena. Uspešno konvertovano: {converted}/{len(csv_files)} fajlova. Preskočeno: {skipped}.")
        log.info(f"📂 Mali Parquet fajlovi sačuvani u: {abs_parquet_dir}")

        conversion_in_progress = False

if __name__ == "__main__":
    convert_all_csv_to_parquet()
