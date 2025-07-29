import os
from logs.logger import log
from utils.indicator_data import get_live_indicators
from utils.model_predictor import predict_trade
from utils.db_manager import insert_decision, insert_simulated_trade
from utils.trading_control import (
    pause_trading, resume_trading, is_trading_paused, get_pause_reason
)
from utils.volume_volatility_predictor import predict_volume_volatility
from utils.notifier import notify_pause_due_to_news, notify_resume_due_to_news
from utils.program_state import is_program_running

# Dodato za guard na download/konverziju:
from data.downloader.dukascopy_downloader import download_in_progress
from utils.converter import conversion_in_progress

# Dodato za vesti/sentiment:
from utils.settings_handler import load_settings
from utils.news_state import (
    analyze_and_update_sentiment, get_news_pause_state
)
from utils.news_fetcher import fetch_latest_news  # mora vraćati listu dict-ova sa 'title' i 'summary'

AI_FEATURES = [
    "rsi", "macd", "ema10", "ema30", "close", "volume", "spread",
    "adx", "stochastic", "cci", "gold_trend"
]

def run_strategy():
    try:
        from ui.signal_status import update_signal_lamp

        # --- Guard: ne radi dok god traje download ili konverzija ---
        if download_in_progress or conversion_in_progress:
            log.info("⚠️ Strategija preskočena – podaci se još preuzimaju/konvertuju.")
            return

        # --- Prvo: PROVERI VESTI I FILTRIRAJ PO KLJUČNIM REČIMA ---
        settings = load_settings()
        keywords = settings.get("news_keywords", [])
        latest_news = fetch_latest_news()  # očekuje listu {'title':..., 'summary':...}

        relevant_sentiment = "neutral"
        relevant_news_found = False
        for news in latest_news:
            sentiment = analyze_and_update_sentiment(
                news_title=news.get("title", ""),
                news_summary=news.get("summary", ""),
                keywords=keywords
            )
            if sentiment in ("panic", "fear"):
                relevant_sentiment = sentiment
                relevant_news_found = True
                break
            elif sentiment in ("positive", "neutral"):
                relevant_news_found = True

        if relevant_news_found and relevant_sentiment in ("panic", "fear"):
            pause_trading(reason="news")
            update_signal_lamp("red", f"Vesti: {relevant_sentiment}")
            notify_pause_due_to_news()
            log.warning(f"🚨 Trgovanje PAUZIRANO zbog vesti ({relevant_sentiment})!")
            return
        elif get_news_pause_state():
            # otpauziraj samo ako je pauza zbog vesti
            resume_trading(reason="news")
            update_signal_lamp("green", "Vesti: ok")
            notify_resume_due_to_news()
            log.info("🟢 Trgovanje nastavljeno – vesti više nisu opasne.")

        # --- Provera globalne pauze ---
        if is_trading_paused():
            reason = get_pause_reason()
            label = "Pauzirano: vesti" if reason == "news" else "Pauzirano: volatilnost"
            update_signal_lamp("red", label)
            log.info(f"⏸️ Trgovanje je pauzirano – razlog: {reason}")
            return

        log.info("📈 Strategija se izvršava...")

        # --- Live indikatori ---
        indicator_data = get_live_indicators("XAUUSD")
        if not indicator_data:
            log.warning("⚠️ Nema dostupnih indikatora za XAUUSD.")
            update_signal_lamp("yellow", "Nedostaju indikatori")
            return

        # --- Volumen/volatilnost ---
        vol, vola, err = predict_volume_volatility()
        if err:
            log.warning(f"⚠️ Vol/Vol predikcija: {err}")
            update_signal_lamp("yellow", "Greška u predikciji vol/vola")
        else:
            log.info(f"🔎 Predikcija: Volume={vol}, Volatility={vola}")
            if vola >= 0.02:
                pause_trading(reason="volatility")
                update_signal_lamp("red", f"Volatilnost visoka ({vola:.3f})")
                notify_pause_due_to_news()
                log.warning("🚫 Trgovanje pauzirano zbog visoke volatilnosti.")
                return
            elif vola >= 0.01:
                update_signal_lamp("yellow", f"Volatilnost srednja ({vola:.3f})")
            else:
                update_signal_lamp("green", f"Volatilnost niska ({vola:.3f})")

        # otpauziraj ako je bila pauza zbog volatilnosti
        resume_trading(reason="volatility")
        notify_resume_due_to_news()

        # --- AI predikcija ---
        input_data = {feat: indicator_data.get(feat, 0) for feat in AI_FEATURES}
        missing = [feat for feat, v in input_data.items() if v is None]
        if missing:
            log.warning(f"⚠️ Nedostaju AI feature-i: {missing}")
            update_signal_lamp("yellow", "AI: Nedostaju feature-i")
            return

        decision = predict_trade(**input_data)
        if not decision or decision == "N/A":
            update_signal_lamp("yellow", "AI još ne daje signal")
            log.warning("🔶 AI još nije spreman – nedovoljno podataka.")
            return

        log.info(f"🤖 AI predikcija: {decision}")

        # --- Simulacija ili realan trejd ---
        if not is_program_running():
            insert_simulated_trade(
                symbol="XAUUSD",
                decision=str(decision),
                indicators=input_data
            )
            insert_decision("XAUUSD", decision.lower(), explanation=str(input_data), result="simulated")
            log.info("🟢 Simulirani trejd upisan (posmatranje).")
            return

        insert_decision("XAUUSD", decision.lower(), explanation=str(input_data), result="pending")
        # ovde bi išlo otvaranje pozicije

    except Exception as e:
        try:
            from ui.signal_status import update_signal_lamp
            update_signal_lamp("red", "Greška u strategiji")
        except Exception:
            pass
        log.error(f"❌ Greška u strategiji: {e}")
