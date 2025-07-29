import sys
import os
import time
import threading
import logging
from PyQt5 import QtWidgets

from utils.settings_handler import load_settings, save_settings
from backend.mt5_connector import connect_to_mt5
from logs.logger import log
from utils.config_validator import validate_config
from utils.scheduler import start_scheduler
from scheduler.strategy_scheduler import start_strategy_scheduler
from ai.trainer import manual_train_full_model, ai_training_in_progress, daily_model_backup
from utils.model_predictor import predict_trade
from utils.data_helper import get_statistics_by_symbol, get_total_trade_count, insert_decision
from utils.news_monitor import start_news_monitor
from utils.news_state import get_news_pause_state, get_sentiment_state
from ui.dashboard import DashboardWindow
from utils.converter_scheduler import start_daily_converter_scheduler
from data.downloader.dukascopy_downloader import start_parallel_download, download_in_progress
from tools.csv_to_parquet_batch import convert_all_csv_to_parquet
from tools.merge_all_parquet import merge_all_parquet
from tools.parquet_resample import ALLOWED_TIMEFRAMES, resample_parquet_selected
from tools.generate_trade_history import generate_trade_history
from tools.generate_trade_features import generate_trade_features
from utils.converter import conversion_in_progress

# Missing-data backfill system
from data_ingest.missing_data_backfill_system import DataIngestor, DataStore

logging.getLogger("apscheduler").setLevel(logging.ERROR)

TIMEFRAME_MODES = {
    "scalping": ["M1", "M5", "M15"],
    "daily":   ["M15", "M30", "H1"],
}

def get_mode_and_timeframes():
    settings = load_settings()
    mode = settings.get("mode", "scalping").lower().strip()
    if mode not in TIMEFRAME_MODES:
        log.warning(f"⚠️ Nevalidan mod: '{mode}', prebacujem na 'scalping'.")
        mode = "scalping"
        settings["mode"] = mode
        save_settings(settings)
    selected_timeframes = {
        tf: ALLOWED_TIMEFRAMES[tf]
        for tf in TIMEFRAME_MODES[mode]
        if tf in ALLOWED_TIMEFRAMES
    }
    return mode, selected_timeframes

MODE, SELECTED_TIMEFRAMES = get_mode_and_timeframes()

download_lock   = threading.Lock()
conversion_lock = threading.Lock()
ai_lock         = threading.Lock()

class ProcessStatus:
    def __init__(self):
        self.status = {"download": False, "conversion": False, "ai": False}
        self.lock = threading.Lock()
    def set(self, proc, busy):
        with self.lock:
            self.status[proc] = busy
    def is_busy(self):
        with self.lock:
            return any(self.status.values())
    def active_before(self, proc):
        order = ["download", "conversion", "ai"]
        idx = order.index(proc)
        with self.lock:
            return any(self.status[o] for o in order[:idx])

PROC_STATUS = ProcessStatus()

def periodic_status_logger():
    while True:
        msgs = []
        for proc, busy in PROC_STATUS.status.items():
            if busy:
                msgs.append({
                    "download":   "⏳ Download je u toku...",
                    "conversion": "🔄 Konverzija je u toku...",
                    "ai":         "🧠 AI trening u toku..."
                }[proc])
        if msgs:
            log.info(" | ".join(msgs))
        time.sleep(1)

def main():
    print("==> Ulazim u main()")
    threading.Thread(target=periodic_status_logger, daemon=True).start()
    print("==> Status logger startovan")

    if not validate_config():
        log.error("⛔ Konfiguracija nije validna. Zatvaram aplikaciju.")
        return
    print("==> Konfiguracija je validna")

    settings = load_settings()
    print("==> Podešavanja učitana")
    for key in ("path", "login", "password", "server"):
        if not settings.get(key):
            log.error("❌ Nedostaju MT5 parametri u konfiguraciji.")
            return

    if not connect_to_mt5(
        settings["path"],
        int(settings["login"]),
        settings["password"],
        settings["server"]
    ):
        log.error("❌ MT5 konekcija neuspešna.")
        return
    print("==> Uspešno konektovan na MT5")

    start_news_monitor()
    print("==> Novinski monitor startovan")

    if get_news_pause_state():
        log.warning("🚨 Trgovanje je PAUZIRANO zbog vesti.")
    log.info("✅ Trgovanje dozvoljeno.")
    log.info(f"📊 Sentiment tržišta: {get_sentiment_state().upper()}")
    print("==> Trgovanje dozvoljeno")

    # ======= OVAJ DEO MORA DA POSTOJI, OVO JE TVOJA VERZIJA =======
    db_path = settings.get("data_db_path", "local.duckdb")
    store = DataStore(db_path=db_path)
    ingestor = DataIngestor(
        symbol=settings.get("symbol", "EURUSD"),
        timeframe=settings.get("timeframe", "M1"),
        store=store
    )
    ingestor.start()
    print("==> DataIngestor startovan")

    trade_count = get_total_trade_count()
    train_freq  = int(settings.get("ai_training_frequency", 100))
    if trade_count > 0 and trade_count % train_freq == 0:
        threading.Thread(target=manual_train_full_model, daemon=True).start()
    print("==> AI training check odrađen")

    try:
        for s in get_statistics_by_symbol():
            log.info(
                f"📈 Statistika za {s['symbol']}: profit={s['total_profit']} USD, ukupno={s['total_trades']}"
            )
    except Exception as e:
        log.warning(f"⚠️ Ne mogu dohvatiti statistiku: {e}")
    print("==> Statistika prikazana")

    start_scheduler()
    start_strategy_scheduler()
    print("==> Scheduleri pokrenuti")

    log.info(
        f"🚀 Pokrećem GUI... (MODE: {MODE.upper()}, Timeframes: {', '.join(SELECTED_TIMEFRAMES.keys())})"
    )
    print("==> Pozivam GUI")

    try:
        app    = QtWidgets.QApplication(sys.argv)
        print("==> QApplication instanciran")
        window = DashboardWindow(settings)
        print("==> DashboardWindow kreiran")
        window.show()
        print("==> window.show() pozvan")

        threading.Thread(target=start_daily_converter_scheduler, args=(2, 0), daemon=True).start()
        threading.Thread(target=daily_model_backup, daemon=True).start()

        sys.exit(app.exec_())
    except Exception as e:
        log.error(f"❌ Greška u GUI: {e}")
        print(f"❌ GUI ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
