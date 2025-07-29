import logging
import os
import shutil
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# 📁 Putanje za log fajlove
LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")
MODEL_LOG_DIR = os.path.join(LOG_DIR, "models")

# ✅ Osiguraj postojanje foldera
for path in [LOG_DIR, ARCHIVE_DIR, MODEL_LOG_DIR]:
    os.makedirs(path, exist_ok=True)

# 📦 Arhiviranje starih logova
def archive_old_logs():
    today_str = datetime.now().strftime('%Y-%m-%d')
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if (
            filename.endswith(".log")
            and today_str not in filename
            and not os.path.isdir(file_path)
        ):
            dst_path = os.path.join(ARCHIVE_DIR, filename)
            try:
                shutil.move(file_path, dst_path)
            except Exception as e:
                print(f"⚠️ Ne mogu da arhiviram log: {filename} – {e}", flush=True)

archive_old_logs()

# 📅 Nazivi log fajlova po datumu
date_str = datetime.now().strftime('%Y-%m-%d')
INFO_LOG_PATH = os.path.join(LOG_DIR, f"izvor_{date_str}.log")
ERROR_LOG_PATH = os.path.join(LOG_DIR, f"errors_{date_str}.log")
CRITICAL_LOG_PATH = os.path.join(LOG_DIR, f"critical_{date_str}.log")
ALERTS_LOG_PATH = os.path.join(LOG_DIR, "trading_alerts.log")

# 🧠 Glavni logger
log = logging.getLogger("IzvorLogger")
log.setLevel(logging.DEBUG)

# 🧼 Očisti stare handlere ako već postoje
if log.hasHandlers():
    for handler in list(log.handlers):
        log.removeHandler(handler)

# 🧾 Format log poruka
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ➕ Funkcija za dodavanje handlera
def add_handler(path, level, formatter, rotating=True, max_bytes=5_000_000, backups=3):
    try:
        if rotating:
            handler = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
        else:
            handler = logging.FileHandler(path, encoding="utf-8")
        handler.setLevel(level)
        handler.setFormatter(formatter)
        log.addHandler(handler)
    except Exception as e:
        print(f"⚠️ Ne mogu da upišem u log fajl {path}: {e}", flush=True)

# 📂 Glavni log fajlovi
add_handler(INFO_LOG_PATH, logging.DEBUG, formatter, rotating=True, max_bytes=5_000_000, backups=3)
add_handler(ERROR_LOG_PATH, logging.ERROR, formatter, rotating=True, max_bytes=2_000_000, backups=2)
add_handler(CRITICAL_LOG_PATH, logging.CRITICAL, formatter, rotating=False)
add_handler(ALERTS_LOG_PATH, logging.WARNING, formatter, rotating=True, max_bytes=2_000_000, backups=5)

# 🖥️ Console log
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

log.info(f"🚀 Pokrenut log sistem (fajlovi: {INFO_LOG_PATH}, {ERROR_LOG_PATH})")

# 🧠 Model logger – pojedinačno po imenu modela
def get_model_logger(model_name: str):
    logger = logging.getLogger(f"model_{model_name}")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        log_file = os.path.join(MODEL_LOG_DIR, f"{model_name}.log")
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
