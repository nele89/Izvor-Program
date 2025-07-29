import os
import threading
from datetime import datetime
from data.downloader.histdata_http_downloader import download_and_save

SYMBOLS = [
    "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
    "AUDUSD", "NZDUSD", "USDCAD", "BTCUSD", "ETHUSD"
]

TIMEFRAMES = {
    "M1": "60",
    "M5": "300",
    "M15": "900",
    "M30": "1800",
    "H1": "3600",
    "H4": "14400",
    "D1": "86400"
}

BASE_DIR = os.path.join("data", "dukascopy")
MAX_AGE_DAYS = 3

def is_file_outdated(path):
    if not os.path.exists(path):
        return True
    last_modified = datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.utcnow() - last_modified).days > MAX_AGE_DAYS

def check_and_update_database():
    print("🔍 Pozadinska provera baze...")
    for symbol in SYMBOLS:
        for tf_name, tf_code in TIMEFRAMES.items():
            today = datetime.utcnow()
            file_path = os.path.join(BASE_DIR, symbol, f"{symbol}_{tf_name}_{today.year}_{today.month:02d}.csv")
            if is_file_outdated(file_path):
                print(f"⏬ Osvežavanje: {symbol} {tf_name}")
                threading.Thread(
                    target=download_and_save,
                    args=(symbol, tf_name, tf_code, today.year, today.month),
                    daemon=True
                ).start()

def run_background_database_check():
    thread = threading.Thread(target=check_and_update_database, daemon=True)
    thread.start()
