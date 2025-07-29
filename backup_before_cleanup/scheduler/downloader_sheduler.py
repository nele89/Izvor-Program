import threading
import time
from datetime import datetime, timedelta

from data.downloader.dukascopy_downloader import start_parallel_download
from utils.settings_handler import load_settings
from logs.logger import log

def should_download_now(hour=2, minute=0):
    now = datetime.now()
    return now.hour == hour and now.minute == minute

def start_downloader_scheduler(check_interval=60):
    """
    Pokreće Dukascopy downloader svaku noć u 02:00 (ili kako podesiš sat/minut).
    """
    def scheduler_loop():
        last_run = None
        while True:
            now = datetime.now()
            # Proveri da li je vreme za novo skidanje (i da li je već pokrenuto za taj dan)
            if should_download_now(hour=2, minute=0):
                if not last_run or last_run.date() != now.date():
                    log.info("🕑 Vreme je za automatsko skidanje podataka (02:00)...")
                    settings = load_settings()
                    start_parallel_download(settings)
                    last_run = now
            time.sleep(check_interval)

    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    log.info("📅 Downloader scheduler je pokrenut u pozadini (02:00 svake noći).")

if __name__ == "__main__":
    start_downloader_scheduler()
    while True:
        time.sleep(60)
