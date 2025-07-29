import os
import pandas as pd
import shutil
import joblib
import threading
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from apscheduler.schedulers.background import BackgroundScheduler

from logs.logger import log
from utils.paths import MODEL_DIR
from utils.db_manager import get_training_data
from utils.settings_handler import load_settings

# Dinamički odredi putanju modela na osnovu moda iz podešavanja
settings = load_settings()
mode = settings.get("mode", "scalping").lower().strip()
model_filename = f"model_{mode}.pkl"
MODEL_PATH = os.path.join(MODEL_DIR, model_filename)
TRAIN_LOG = os.path.join(MODEL_DIR, "ai_train_log.json")
BACKUP_DIR = os.path.join(MODEL_DIR, "backups")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

FEATURE_ORDER = [
    "rsi", "macd", "ema10", "ema30", "close", "volume", "spread",
    "adx", "stochastic", "cci", "gold_trend"
]

ai_training_in_progress = False
ai_training_lock = threading.Lock()
backup_thread_started = False

def backup_file(src, suffix=".bak"):
    if os.path.exists(src):
        bak_path = src + suffix
        try:
            shutil.copy2(src, bak_path)
            log.info(f"🗂️ Backup: {bak_path}")
        except Exception as e:
            log.warning(f"❌ Ne mogu da napravim backup za {src}: {e}")

def save_ai_train_log(rows_trained, model_path=MODEL_PATH, accuracy=None, msg=None):
    log_data = {}
    if os.path.exists(TRAIN_LOG):
        try:
            with open(TRAIN_LOG, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception:
            log_data = {}
    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "model_file": os.path.basename(model_path),
        "model_size": os.path.getsize(model_path) if os.path.exists(model_path) else 0,
        "rows_trained": rows_trained,
        "accuracy": accuracy,
        "msg": msg
    }
    log_data[record["time"]] = record
    backup_file(TRAIN_LOG, ".bak")
    try:
        with open(TRAIN_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        log.info(f"📝 Upisan trening log za {record['time']}")
    except Exception as e:
        log.warning(f"❌ Ne mogu da upišem trening log: {e}")

def _train_model(df, model_path=MODEL_PATH):
    for feat in FEATURE_ORDER:
        if feat not in df.columns:
            df[feat] = 0

    if "gold_trend" not in df.columns or df["gold_trend"].isnull().all():
        if "ema10" in df.columns and "ema30" in df.columns:
            df["gold_trend"] = (
                (df["ema10"] > df["ema30"]).astype(int) -
                (df["ema10"] < df["ema30"]).astype(int)
            )
        else:
            df["gold_trend"] = 0

    df = df.dropna(subset=FEATURE_ORDER + ["label"])

    if len(df) < 120:
        log.warning(f"⚠️ Premalo podataka za trening modela ({len(df)} redova).")
        save_ai_train_log(len(df), msg="Premalo podataka")
        return

    X = df[FEATURE_ORDER]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    backup_file(model_path)
    joblib.dump(model, model_path)
    log.info(f"✅ AI model sačuvan: {model_path}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(BACKUP_DIR, f"model_{timestamp}.pkl")
    joblib.dump(model, backup_path)
    log.info(f"🗂️ Backup modela: {backup_path}")

    accuracy = model.score(X, y)
    save_ai_train_log(rows_trained=len(X), accuracy=accuracy)
    log.info(f"🧠🔵 KRAJ: AI trening završen ({len(X)} redova) – Preciznost: {accuracy:.4f}")

def initial_train_if_needed():
    if not os.path.exists(MODEL_PATH):
        log.info("🟢 Inicijalni trening modela (prvo pokretanje)...")
        df = get_training_data()
        if df is None or df.empty:
            log.warning("⚠️ Nema podataka za inicijalni trening.")
            return
        if len(df) > 200_000:
            df = df.tail(200_000).copy()
        _train_model(df)

def train_full_model():
    global ai_training_in_progress
    with ai_training_lock:
        if ai_training_in_progress:
            log.info("🧠 AI trening je već u toku.")
            return
        ai_training_in_progress = True
    try:
        log.info("🧠🟢 Full trening na 15 dana...")
        df = get_training_data()
        if df is None or df.empty:
            log.warning("⚠️ Nema dovoljno podataka za treniranje AI modela.")
            save_ai_train_log(0, msg="Nema podataka (15 dana)")
            return
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df[df["timestamp"] >= datetime.now() - timedelta(days=15)]
        if len(df) > 200_000:
            log.info(f"📉 Ograničavam podatke na poslednjih 200000 redova (od ukupno {len(df)}) za full trening.")
            df = df.tail(200_000).copy()
        _train_model(df)
    except Exception as e:
        log.error(f"❌ Greška u full treningu: {e}")
        save_ai_train_log(0, msg=f"Full: {e}")
    finally:
        with ai_training_lock:
            ai_training_in_progress = False

def train_refresh_model():
    global ai_training_in_progress
    with ai_training_lock:
        if ai_training_in_progress:
            log.info("🧠 AI trening je već u toku.")
            return
        ai_training_in_progress = True
    try:
        log.info("🧠🟢 Refresh trening na 24h...")
        df = get_training_data()
        if df is None or df.empty:
            log.warning("⚠️ Nema dovoljno podataka za treniranje AI modela.")
            save_ai_train_log(0, msg="Nema podataka (24h)")
            return
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df[df["timestamp"] >= datetime.now() - timedelta(days=1)]
        if len(df) > 2_000:
            log.info(f"📉 Ograničavam podatke na poslednjih 2000 redova (od ukupno {len(df)}) za refresh trening.")
            df = df.tail(2_000).copy()
        _train_model(df)
    except Exception as e:
        log.error(f"❌ Greška u refresh treningu: {e}")
        save_ai_train_log(0, msg=f"Refresh: {e}")
    finally:
        with ai_training_lock:
            ai_training_in_progress = False

def manual_train_full_model():
    global ai_training_in_progress
    with ai_training_lock:
        if ai_training_in_progress:
            log.info("🧠 Manualni trening je već u toku.")
            return
        ai_training_in_progress = True
    t = threading.Thread(target=train_full_model, daemon=True)
    t.start()

def daily_model_backup():
    import time
    while True:
        now = datetime.now()
        if now.hour == 23 and now.minute == 59:
            try:
                if os.path.exists(MODEL_PATH):
                    day_stamp = now.strftime("%Y-%m-%d")
                    daily_backup = os.path.join(BACKUP_DIR, f"model_daily_{day_stamp}.pkl")
                    shutil.copy2(MODEL_PATH, daily_backup)
                    log.info(f"📅 Dnevni backup: {daily_backup}")
            except Exception as e:
                log.error(f"❌ Greška pri dnevnom backupu: {e}")
            time.sleep(60)
        else:
            time.sleep(30)

def start_daily_backup_thread():
    global backup_thread_started
    if not backup_thread_started:
        threading.Thread(target=daily_model_backup, daemon=True).start()
        backup_thread_started = True

def start_ai_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(train_full_model, 'cron', hour=8, minute=0, id="ai_full_retrain", replace_existing=True)
    scheduler.add_job(train_refresh_model, 'interval', hours=1, id="ai_hourly_refresh", replace_existing=True)
    scheduler.start()
    log.info("⏰ AI scheduler pokrenut: Full trenira u 8h, refresh na 24h svakih 1h.")

if __name__ == "__main__":
    initial_train_if_needed()
    start_daily_backup_thread()
    start_ai_scheduler()
    # Samo za testiranje – ručno pokretanje treninga
    train_full_model()
    train_refresh_model()
