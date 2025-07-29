import sys
import os
import time
import threading
import requests
import struct
import pandas as pd
import json
from datetime import datetime, timedelta

from logs.logger import log
from utils.settings_handler import load_settings
from tools.csv_to_parquet import csv_folder_to_parquet
from tools.merge_all_parquet import merge_all_parquet
from tools.parquet_resample import resample_parquet_all
from tools.conversion_utils import need_convert_csv_to_parquet, need_merge_parquet, need_resample

BASE_URL = "https://datafeed.dukascopy.com/datafeed"
DEFAULT_PAUSE = 0.5
DEFAULT_FOLDER = os.path.join("data", "dukascopy", "XAUUSD")
DEFAULT_START_DATE = datetime(2010, 1, 1)
DEFAULT_END_DATE = datetime.utcnow()
DOWNLOAD_LOG = os.path.join("data", "dukascopy", "download_log.json")

download_lock = threading.Lock()
conversion_lock = threading.Lock()
merge_lock = threading.Lock()
resample_lock = threading.Lock()

download_in_progress = False

def load_download_log():
    if os.path.exists(DOWNLOAD_LOG):
        try:
            with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_download_log(log_data):
    try:
        with open(DOWNLOAD_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as ex:
        log.warning(f"❌ Ne mogu da upišem download_log: {ex}")

def _download_status_reporter():
    while download_in_progress:
        log.info("📥 Download podataka u toku...")
        time.sleep(15)

def is_connected():
    try:
        requests.get("https://www.google.com/", timeout=5)
        return True
    except:
        return False

def download_bin(symbol, dt):
    try:
        year, month, day, hour = dt.year, dt.month - 1, dt.day, dt.hour
        url = f"{BASE_URL}/{symbol.upper()}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.content
        records = []
        prev_ask = prev_bid = 0

        for i in range(0, len(data), 20):
            chunk = data[i:i + 20]
            if len(chunk) < 20:
                continue
            ms, ask, bid, ask_vol, bid_vol = struct.unpack('>IIIII', chunk)
            timestamp = dt + timedelta(milliseconds=ms)
            abs_ask = (prev_ask + ask) / 100000.0
            abs_bid = (prev_bid + bid) / 100000.0
            prev_ask += ask
            prev_bid += bid
            volume = ask_vol + bid_vol
            records.append((timestamp, abs_ask, abs_bid, volume))

        return records
    except Exception as e:
        log.warning(f"⚠️ Greška za {symbol} {dt.strftime('%Y-%m-%d %H:%M')}: {e}")
        return None

def find_resume_date(symbol, start_date, end_date, folder, download_log):
    if not os.path.exists(folder):
        return start_date

    times = []
    for fname, meta in download_log.items():
        try:
            if fname.startswith(symbol):
                dt = datetime.strptime(fname.split("_")[1], "%Y-%m-%d-%H")
                times.append(dt)
        except:
            continue
    latest = max(times) if times else None

    if latest and latest < end_date:
        return latest + timedelta(hours=1)
    return start_date

def run_conversion_if_needed(folder):
    with conversion_lock:
        if need_convert_csv_to_parquet():
            log.info("🔄 CSV → Parquet konverzija u toku...")
            try:
                csv_folder_to_parquet(folder)
                log.info("✅ CSV → Parquet konverzija završena.")
            except Exception as e:
                log.error(f"❌ Greška tokom CSV → Parquet konverzije: {e}")
        else:
            log.info("✅ CSV → Parquet već ažuran.")

def run_merge_if_needed():
    with merge_lock:
        if need_merge_parquet():
            log.info("🔄 Merge Parquet fajlova u toku...")
            try:
                merge_all_parquet()
                log.info("✅ Merge završen.")
            except Exception as e:
                log.error(f"❌ Greška tokom merge: {e}")
        else:
            log.info("✅ Parquet merge već ažuran.")

def run_resample_if_needed():
    with resample_lock:
        if need_resample():
            log.info("🔄 Resample Parquet fajlova u toku...")
            try:
                resample_parquet_all()
                log.info("✅ Resample završen.")
            except Exception as e:
                log.error(f"❌ Greška tokom resample: {e}")
        else:
            log.info("✅ Resample fajlovi već ažurni.")

def run_all_conversion_steps(folder):
    # SVE IDE REDOM, BLOKIRANO, NIŠTA PARALELNO!
    run_conversion_if_needed(folder)
    run_merge_if_needed()
    run_resample_if_needed()

def download_symbol(symbol, start_date, end_date, folder, pause):
    global download_in_progress
    with download_lock:
        download_in_progress = True
        threading.Thread(target=_download_status_reporter, daemon=True).start()

        os.makedirs(folder, exist_ok=True)
        download_log = load_download_log()
        current = find_resume_date(symbol, start_date, end_date, folder, download_log)
        if current > end_date:
            log.info(f"✅ Sve već preuzeto za {symbol}.")
            download_in_progress = False
            return

        count_files = 0
        skipped = 0

        while current <= end_date:
            file_name = f"{symbol}_{current.strftime('%Y-%m-%d-%H')}.csv"
            file_path = os.path.join(folder, file_name)

            already_logged = (
                file_name in download_log and
                os.path.exists(file_path)
            )
            if already_logged:
                skipped += 1
                current += timedelta(hours=1)
                continue

            if not is_connected():
                log.error("⛔ Nema interneta. Pokušavam ponovo za 30 sekundi...")
                time.sleep(30)
                continue

            ticks = download_bin(symbol, current)
            if ticks:
                df = pd.DataFrame(ticks, columns=["time", "ask", "bid", "volume"])
                df["spread"] = df["ask"] - df["bid"]
                df.to_csv(file_path, index=False)
                download_log[file_name] = {
                    "timestamp": int(os.path.getmtime(file_path)),
                    "rows": len(df),
                    "size": os.path.getsize(file_path)
                }
                save_download_log(download_log)
                log.info(f"✅ Sačuvano: {file_name} ({len(df)} redova)")
                count_files += 1
            else:
                if os.path.exists(file_path) and os.path.getsize(file_path) < 100:
                    os.remove(file_path)
                log.info(f"⚠️ Nema podataka za {symbol} {current.strftime('%Y-%m-%d %H:%M')}")

            current += timedelta(hours=1)
            time.sleep(pause)

        run_all_conversion_steps(folder)
        download_in_progress = False
        log.info(f"🏁 {symbol}: Preuzimanje završeno. Novi fajlovi: {count_files}, preskočeno: {skipped}")

def start_parallel_download(settings=None, start_date=None, end_date=None, pause=None):
    log.info("🚀 Pokrećem Dukascopy downloader (XAUUSD)...")

    if not settings:
        settings = load_settings()

    config = settings.get("dukascopy", {})
    folder = config.get("target_folder", DEFAULT_FOLDER)
    pause = pause if pause is not None else float(config.get("pause_seconds", DEFAULT_PAUSE))

    try:
        start_date = start_date or datetime.fromisoformat(config.get("start_date", DEFAULT_START_DATE.isoformat()))
    except Exception as e:
        log.error(f"❌ Neispravan start_date: {e}")
        start_date = DEFAULT_START_DATE

    try:
        end_date = end_date or datetime.fromisoformat(config.get("end_date", DEFAULT_END_DATE.isoformat()))
    except Exception as e:
        log.error(f"❌ Neispravan end_date: {e}")
        end_date = DEFAULT_END_DATE

    # Samo jedan download proces u isto vreme!
    t = threading.Thread(target=download_symbol, args=("XAUUSD", start_date, end_date, folder, pause), daemon=True)
    t.start()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Paralelni Dukascopy downloader")
    parser.add_argument("--pause", type=float, default=0.5, help="Pauza u sekundama između zahteva")
    args = parser.parse_args()
    start_parallel_download(pause=args.pause)
