import os
import json
from logs.logger import log

CSV_FOLDER = os.path.join("data", "dukascopy", "XAUUSD")
PARQUET_FOLDER = os.path.join("data", "dukascopy")
PARQUET_RAW_FOLDER = os.path.join(PARQUET_FOLDER, "parquet_raw")
PARQUET_MASTER_FILE = os.path.join(PARQUET_FOLDER, "trade_history.parquet")
PARQUET_RESAMPLED_FOLDER = os.path.join(PARQUET_FOLDER, "parquet_resampled")

CONVERT_LOG = os.path.join(PARQUET_FOLDER, "convert_log.json")
MERGE_LOG = os.path.join(PARQUET_FOLDER, "merge_log.json")
RESAMPLE_LOG = os.path.join(PARQUET_FOLDER, "resample_log.json")

def _load_json_log(log_path):
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log.warning(f"⚠️ Ne mogu da učitam log ({log_path}): {e}")
    return {}

def need_convert_csv_to_parquet():
    convert_log = _load_json_log(CONVERT_LOG)
    from glob import glob
    csv_files = [os.path.basename(f) for f in glob(os.path.join(CSV_FOLDER, "*.csv"))]
    if convert_log:
        for csv_file in csv_files:
            path = os.path.join(CSV_FOLDER, csv_file)
            mtime = int(os.path.getmtime(path))
            prev = convert_log.get(csv_file, {})
            # podržava star format (samo mtime) i novi (dict)
            if isinstance(prev, dict):
                if prev.get("csv_mtime") != mtime:
                    return True
            else:
                if prev != mtime:
                    return True
        return False

    # Legacy fallback
    if not csv_files:
        return False
    if not os.path.exists(PARQUET_MASTER_FILE):
        return True
    parquet_mtime = os.path.getmtime(PARQUET_MASTER_FILE)
    return any(os.path.getmtime(os.path.join(CSV_FOLDER, f)) > parquet_mtime for f in csv_files)

def need_merge_parquet():
    merge_log = _load_json_log(MERGE_LOG)
    from glob import glob
    pq_files = [os.path.basename(f) for f in glob(os.path.join(PARQUET_RAW_FOLDER, "*.parquet"))]
    if merge_log:
        last_files = merge_log.get("last_files", {})
        for pq_file in pq_files:
            path = os.path.join(PARQUET_RAW_FOLDER, pq_file)
            mtime = int(os.path.getmtime(path))
            if last_files.get(pq_file, 0) != mtime:
                return True
        if not os.path.exists(PARQUET_MASTER_FILE):
            return True
        return False

    if not pq_files:
        return False
    if not os.path.exists(PARQUET_MASTER_FILE):
        return True
    master_mtime = os.path.getmtime(PARQUET_MASTER_FILE)
    return any(os.path.getmtime(os.path.join(PARQUET_RAW_FOLDER, f)) > master_mtime for f in pq_files)

def need_resample():
    resample_log = _load_json_log(RESAMPLE_LOG)
    resampled_files = ["trade_history_M1.parquet", "trade_history_M5.parquet", "trade_history_H1.parquet"]
    if resample_log:
        master_mtime = resample_log.get("master_mtime", 0)
        if not os.path.exists(PARQUET_MASTER_FILE):
            return True
        if int(os.path.getmtime(PARQUET_MASTER_FILE)) != master_mtime:
            return True
        for tf_file in resampled_files:
            tf_key = tf_file.replace("trade_history_", "").replace(".parquet", "")
            out_path = os.path.join(PARQUET_RESAMPLED_FOLDER, tf_file)
            tf_info = resample_log.get("outputs", {}).get(tf_key, {})
            if not os.path.exists(out_path):
                return True
            if tf_info and int(os.path.getmtime(out_path)) != tf_info.get("mtime", 0):
                return True
        return False

    if not os.path.exists(PARQUET_RESAMPLED_FOLDER):
        return True
    for fname in resampled_files:
        path = os.path.join(PARQUET_RESAMPLED_FOLDER, fname)
        if not os.path.exists(path):
            return True
    if not os.path.exists(PARQUET_MASTER_FILE):
        return True
    master_mtime = os.path.getmtime(PARQUET_MASTER_FILE)
    return any(os.path.getmtime(os.path.join(PARQUET_RESAMPLED_FOLDER, f)) < master_mtime for f in resampled_files)
