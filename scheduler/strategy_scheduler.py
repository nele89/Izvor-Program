from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logs.logger import log
from strategy.strategy_executor import run_strategy
from utils.settings_handler import load_settings
from utils.news_state import get_news_pause_state

scheduler = BackgroundScheduler()
paused_due_to_news = False

def strategy_job_wrapper():
    global paused_due_to_news

    if get_news_pause_state():
        if not paused_due_to_news:
            log.warning("🚫 Strategija PAUZIRANA zbog negativnih vesti.")
            paused_due_to_news = True
        return
    else:
        if paused_due_to_news:
            log.info("✅ Vesti stabilne – nastavljam strategiju.")
            paused_due_to_news = False

    run_strategy()

def start_strategy_scheduler():
    settings = load_settings()
    try:
        checks_per_second = int(settings.get("checks_per_second", 1))
        if checks_per_second < 1 or checks_per_second > 50:
            log.warning("⚠️ 'checks_per_second' mora biti u opsegu 1–50. Postavljam na podrazumevano 1.")
            checks_per_second = 1
    except Exception:
        log.warning("⚠️ Nevalidan unos za 'checks_per_second'. Postavljam na 1.")
        checks_per_second = 1

    interval = 1.0 / checks_per_second

    scheduler.add_job(
        strategy_job_wrapper,
        "interval",
        seconds=interval,
        id="strategy_job",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()

    log.info(f"🕒 Strategija pokrenuta – proverava se svakih {interval:.2f} sekundi.")
