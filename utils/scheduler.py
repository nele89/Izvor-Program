import os
import shutil
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from logs.logger import log
from utils.monitor_closed import fetch_and_log_closed_trades
from utils.settings_handler import load_settings
from ai.trainer import manual_train_full_model
from utils.market_time import is_market_open
from utils.report_generator_job import report_generator_job
from utils.data_handler_job import data_handler_job
from utils.status_auto_updater import auto_update_status
from data.downloader.dukascopy_downloader import start_parallel_download

scheduler = BackgroundScheduler()

def backup_database():
    try:
        src_path = os.path.join("db", "trading_ai_core.db")
        if not os.path.exists(src_path):
            log.warning("⚠️ Nema baze za backup.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        dst_dir = os.path.join("db", "backups")
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, f"backup_{date_str}.db")
        shutil.copy2(src_path, dst_path)
        log.info(f"💾 Backup baze sačuvan: {dst_path}")
    except Exception as e:
        log.error(f"❌ Greška prilikom backup-a baze: {e}")

def auto_train_ai_model():
    try:
        if is_market_open():
            log.info("🤖 AI auto-trening pokrenut (prema podešenom intervalu)")
            manual_train_full_model()
        else:
            log.info("🕒 AI trening preskočen – tržište zatvoreno")
    except Exception as e:
        log.error(f"❌ Greška u auto-trening funkciji: {e}")

def auto_duka_download():
    try:
        settings = load_settings()
        log.info("⏳ [DUKASCOPY] Automatska provera i download novih fajlova...")
        start_parallel_download(settings)
    except Exception as e:
        log.warning(f"❌ Greška u auto_duka_download: {e}")

def start_scheduler():
    try:
        settings = load_settings()
        refresh_sec = int(settings.get("live_gui_refresh_seconds", 5))
        ai_interval_sec = int(settings.get("ai_training_scheduler_interval", 900))
        if ai_interval_sec < 60:
            log.warning("⚠️ Interval za AI trening je manji od 60 sekundi – koristi se podrazumevanih 900s")
            ai_interval_sec = 900

        jobs = [
            dict(id="log_closed_trades", func=fetch_and_log_closed_trades, trigger="interval", seconds=30),
            dict(id="db_backup", func=backup_database, trigger="interval", hours=2),
            dict(id="ai_auto_training", func=auto_train_ai_model, trigger="interval", seconds=ai_interval_sec),
            dict(id="generate_reports", func=report_generator_job, trigger="cron", hour=1, minute=5),
            dict(id="data_handler_job", func=data_handler_job, trigger="interval", minutes=15),
            dict(id="auto_update_status", func=auto_update_status, trigger="interval", seconds=30),
            dict(id="duka_auto_download", func=auto_duka_download, trigger="interval", minutes=5)
        ]
        # Prvo obrisi postojeće jobove (sigurno pokretanje bez dupliranja)
        existing = set([j.id for j in scheduler.get_jobs()])
        for job in jobs:
            if job['id'] in existing:
                scheduler.remove_job(job['id'])

        for job in jobs:
            scheduler.add_job(
                func=job['func'],
                trigger=job['trigger'],
                id=job['id'],
                replace_existing=True,
                **{k: v for k, v in job.items() if k in ('seconds', 'hours', 'minutes', 'hour', 'minute')}
            )
        if not scheduler.running:
            scheduler.start()
            log.info(
                f"🕒 Scheduler pokrenut – refresh GUI: {refresh_sec}s | zatvoreni trejdovi: 30s | "
                f"backup: 2h | AI trening: {ai_interval_sec}s | report: 1/dan | data handler: 15min | "
                f"status: 30s | dukascopy download: 5min"
            )
    except Exception as e:
        log.error(f"❌ Scheduler nije uspeo da se pokrene: {e}")

