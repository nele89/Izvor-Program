# auto_pipeline.py

import sys
import os
import time
from logs.logger import log
from utils.settings_handler import load_settings
from utils.converter_scheduler import convert_all_ticks
from ai.trainer import train_and_save_model
from backend.ai_analyzer import analyze_data
from utils.report_generator import generate_daily_report

def wait_for_download_threads(threads, timeout=900):
    """Čeka da svi download threadovi završe ili dok ne istekne timeout (sekunde)."""
    start = time.time()
    for t in threads:
        while t.is_alive():
            if time.time() - start > timeout:
                log.error("❌ Download threadovi nisu završili na vreme (timeout).")
                return False
            time.sleep(1)
    return True

def run_pipeline():
    log.info("🚦 [AUTO-PIPELINE] Početak automatizovanog procesa...")

    # 1. Učitaj podešavanja
    settings = load_settings()
    symbols = settings.get("dukascopy", {}).get("symbols", ["XAUUSD", "EURUSD", "USDJPY"])
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",") if s.strip()]
    log.info(f"📥 Simboli za download: {symbols}")

    # 2. Download najnovijih podataka (samo CSV) — dobijamo thread listu
    log.info("⏬ Skidanje podataka sa Dukascopy...")
    from data.downloader.dukascopy_downloader import download_symbol, DEFAULT_FOLDER
    from datetime import datetime

    start_date = settings.get("dukascopy", {}).get("start_date", "2015-01-01T00:00:00")
    end_date = settings.get("dukascopy", {}).get("end_date", "2025-06-30T00:00:00")
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except Exception:
        from datetime import datetime as dtn
        start_dt = dtn(2015, 1, 1)
        end_dt = dtn.utcnow()

    threads = []
    for symbol in symbols:
        import threading
        t = threading.Thread(
            target=download_symbol,
            args=(symbol, start_dt, end_dt, DEFAULT_FOLDER, 0.2),
            daemon=True
        )
        t.start()
        threads.append(t)

    log.info("⏳ Čekam završetak download procesa (svi threadovi)...")
    wait_for_download_threads(threads, timeout=1800)
    log.info("✅ Download CSV fajlova kompletiran.")

    # 3. Konverzija CSV-ova u željene timeframove
    log.info("🔄 Pokrećem konverziju CSV tick podataka u M1/M5/H1...")
    convert_all_ticks()
    log.info("✅ Konverzija podataka završena.")

    # 4. Treniranje AI modela na novim podacima
    log.info("🤖 Pokrećem treniranje AI modela...")
    try:
        train_and_save_model()
        log.info("✅ AI model uspešno treniran na najnovijim podacima.")
    except Exception as e:
        log.error(f"❌ Trening AI modela nije uspeo: {e}")

    # 5. Analiza podataka posle treniranja (opciono)
    try:
        log.info("🔍 Pokrećem analizu podataka (AI analiza)...")
        analyze_data()
        log.info("✅ Analiza podataka završena.")
    except Exception as e:
        log.error(f"❌ Analiza podataka nije uspela: {e}")

    # 6. Generisanje izveštaja (opciono, možeš birati dnevni/nedeljni)
    try:
        log.info("📝 Generišem dnevni izveštaj...")
        today = time.strftime("%Y-%m-%d")
        generate_daily_report(today)
        log.info("✅ Dnevni izveštaj uspešno generisan.")
    except Exception as e:
        log.error(f"❌ Generisanje dnevnog izveštaja nije uspelo: {e}")

    log.info("🏁 [AUTO-PIPELINE] Automatizovani proces završen.")

if __name__ == "__main__":
    run_pipeline()
