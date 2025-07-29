from apscheduler.schedulers.background import BackgroundScheduler
from logs.logger import log
import threading
from ai.trainer.train_trend import train_trend_model
from ai.trainer.train_volatility import train_volatility_model
from ai.trainer.train_sentiment import train_sentiment_model
from ai.trainer.train_orderflow import train_orderflow_model
from ai.trainer.train_meta import train_meta_model
from utils.db_manager import get_training_data, get_meta_training_data

training_lock = threading.Lock()


def run_all_trainings():
    with training_lock:
        try:
            log.info("🧠🔄 Pokrećem sve 4+1 AI trening modele...")

            df = get_training_data()
            if df is None or df.empty:
                log.warning("⚠️ Nema podataka za treniranje osnovnih modela.")
                return

            train_trend_model(df)
            train_volatility_model(df)
            train_sentiment_model(df)  # koristi tekstualni deo df-a ako postoji
            train_orderflow_model(df)

            # META model koristi posebno pripremljen skup
            meta_df = get_meta_training_data()
            if meta_df is not None and not meta_df.empty:
                train_meta_model(meta_df)
            else:
                log.warning("⚠️ Nema podataka za treniranje meta-modela.")

            log.info("✅ Trening svih AI modela završen.")

        except Exception as e:
            log.error(f"❌ Greška u run_all_trainings: {e}")


def start_ai_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_trainings, 'cron', hour=8, minute=0, id="ai_daily_train", replace_existing=True)
    scheduler.start()
    log.info("⏰ AI 4+1 scheduler pokrenut: trenira svaki dan u 08:00h")
