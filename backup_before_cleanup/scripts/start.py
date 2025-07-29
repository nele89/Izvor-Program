from utils.settings_handler import load_settings
from backend.mt5_connector import connect_to_mt5
from ui.dashboard import launch_ui
from logs.logger import log
from utils.scheduler import start_scheduler
from scheduler.strategy_scheduler import start_strategy_scheduler
from utils.config_validator import validate_config

from ai.trainer import start_ai_training as train_and_save_model
from utils.model_predictor import predict_trade

from utils.db_manager import (
    get_statistics_by_symbol,
    get_total_trade_count,
    insert_decision
)

from utils.news_monitor import start_news_monitor
from utils.news_state import get_news_pause_state, get_sentiment_state


def main():
    if not validate_config():
        log.error("⛔ Konfiguracija nije validna. Zatvaram aplikaciju.")
        return

    settings = load_settings()

    mt5_login = settings.get("mt5_login", {})
    required_keys = ["path", "login", "password", "server"]
    if not all(k in mt5_login and mt5_login[k] for k in required_keys):
        log.error("❌ Nedostaju osnovni MT5 parametri u mt5_login sekciji.")
        return

    if not connect_to_mt5(
        mt5_login["path"],
        int(mt5_login["login"]),
        mt5_login["password"],
        mt5_login["server"]
    ):
        log.error("❌ MT5 konekcija neuspešna. Zatvaram aplikaciju.")
        return

    start_news_monitor()

    if get_news_pause_state():
        log.warning("🚨 Trgovanje trenutno pauzirano zbog negativnih vesti.")
    else:
        log.info("✅ Trgovanje dozvoljeno – vesti stabilne.")

    sentiment = get_sentiment_state()
    log.info(f"🧠 Trenutni sentiment tržišta: {sentiment.upper()}")

    trade_count = get_total_trade_count()
    train_frequency = int(settings.get("ai_training_frequency", 100))

    if trade_count > 0 and trade_count % train_frequency == 0:
        log.info(f"📊 Imamo {trade_count} trejdova – treniram AI model...")
        try:
            train_and_save_model()
            log.info("🧠 AI model uspešno treniran.")
        except Exception as e:
            log.warning(f"⚠️ AI model nije treniran: {e}")
    else:
        log.info(f"ℹ️ AI model se trenira svakih {train_frequency} trejdova. Trenutno: {trade_count}")

    example_inputs = {
        "rsi": 28,
        "macd": -0.002,
        "ema_diff": -0.5,
        "volume": 120000,
        "spread": 0.12,
        "volatility": 1.8,
        "dxy_value": 104.25,
        "us30_trend": 1,
        "spx500_trend": -1
    }

    try:
        odluka = predict_trade(**example_inputs)
        log.info(f"🧠 AI odluka za testne inpute: {odluka.upper()}")

        if settings.get("ai_use_decision_memory", True):
            explanation = (
                f"RSI={example_inputs['rsi']}, MACD={example_inputs['macd']}, "
                f"EMA diff={example_inputs['ema_diff']}, Vol={example_inputs['volume']}, "
                f"Spread={example_inputs['spread']}, Volatility={example_inputs['volatility']}, "
                f"DXY={example_inputs['dxy_value']}, US30={example_inputs['us30_trend']}, "
                f"SPX500={example_inputs['spx500_trend']}"
            )
            insert_decision(
                symbol="XAUUSD",
                decision=odluka.lower(),
                explanation=explanation,
                result="pending"
            )
            log.info("📌 AI odluka snimljena u decision memory.")
    except Exception as e:
        log.warning(f"⚠️ Ne mogu da upišem AI odluku ili AI predikcija ne radi: {e}")

    try:
        stats = get_statistics_by_symbol()
        for s in stats:
            log.info(
                f"📈 Statistika za {s['symbol']}: profit={s['total_profit']} USD, "
                f"prosečno={s['avg_profit']} USD, ukupno trejdova={s['total_trades']}"
            )
    except Exception as e:
        log.warning(f"⚠️ Statistika nije dostupna: {e}")

    start_scheduler()
    start_strategy_scheduler()

    log.info("🚀 Pokrećem grafički interfejs...")
    launch_ui(settings)


if __name__ == "__main__":
    main()
