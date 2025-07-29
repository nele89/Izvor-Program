from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from utils.converter import convert_all_ticks
from logs.logger import log

converter_scheduler = BackgroundScheduler()

def start_daily_converter_scheduler(hour=2, minute=0):
    try:
        job = converter_scheduler.get_job("daily_converter_job")
        if job is not None:
            log.info("🕒 Converter job je već zakazan, preskačem ponovno zakazivanje.")
            if not converter_scheduler.running:
                converter_scheduler.start()
            return

        trigger = CronTrigger(hour=hour, minute=minute)
        converter_scheduler.add_job(
            convert_all_ticks,
            trigger=trigger,
            id="daily_converter_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )

        if not converter_scheduler.running:
            converter_scheduler.start()

        log.info(f"🕒 Zakazano automatsko konvertovanje podataka svakog dana u {hour:02d}:{minute:02d}")
    except Exception as e:
        log.error(f"❌ Neuspešno zakazivanje konvertora: {e}")
