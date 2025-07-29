from apscheduler.schedulers.background import BackgroundScheduler
from logs.logger import log
from strategy.strategy_executor import run_strategy
from utils.settings_handler import load_settings

scheduler = BackgroundScheduler()

def start_strategy_scheduler():
    try:
        settings = load_settings()
        checks_per_second = 1
        try:
            checks_per_second = int(settings.get("min_checks_per_second", 1))
            if checks_per_second < 1:
                log.warning("⚠️ min_checks_per_second je manji od 1. Postavljam na 1.")
                checks_per_second = 1
        except (ValueError, TypeError):
            log.warning("⚠️ min_checks_per_second nije validan broj. Postavljam na 1.")
            checks_per_second = 1

        interval = max(1.0 / checks_per_second, 0.1)

        # Ukloni stari posao ako postoji (da ne dupliraš jobove)
        job = scheduler.get_job("strategy_job")
        if job is not None:
            scheduler.remove_job("strategy_job")
            log.info("ℹ️ Stara strategija zaustavljena (refresh job).")

        scheduler.add_job(
            run_strategy,
            trigger="interval",
            seconds=interval,
            id="strategy_job",
            replace_existing=True,
            max_instances=1,  # Obezbedi da nema paralelnog izvršavanja!
            coalesce=True     # Spaja zaostale izvršavanja
        )

        if not scheduler.running:
            scheduler.start()
        log.info(f"🕒 Scheduler pokrenut – strategija se izvršava na svakih {interval:.2f} sekundi.")

    except Exception as e:
        log.error(f"❌ Greška prilikom pokretanja strategije: {e}")

def stop_strategy_scheduler():
    try:
        job = scheduler.get_job("strategy_job")
        if job is not None:
            scheduler.remove_job("strategy_job")
            log.info("⛔ Scheduler zaustavljen.")
        else:
            log.info("ℹ️ Scheduler nije bio aktivan ili ne postoji job zaustavljanja.")
    except Exception as e:
        log.warning(f"⚠️ Scheduler nije aktivan ili ne postoji. ({e})")
