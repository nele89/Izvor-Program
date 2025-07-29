# run_bot.py

from utils.settings_handler import load_settings
from mt5.data_collector import initialize_mt5, shutdown_mt5
from engine.ai_engine import AIBot
from engine.strategy_handler import StrategyHandler
from mt5.mt5_monitor import monitor_and_restart_mt5
from reporting.report_launcher import generate_single_report  # 🆕
from logs.logger import log
from datetime import datetime

def main():
    log.info("📥 Pokreće se run_bot.py...")

    # Učitavanje podešavanja iz config.ini (+ .env ako postoji)
    settings = load_settings()

    # Provera i restart MT5 ako je potrebno
    monitor_and_restart_mt5()

    # Inicijalizacija MT5
    initialized = initialize_mt5(
        path=settings.get("path"),
        login=int(settings.get("login")),
        password=settings.get("password"),
        server=settings.get("server")
    )

    if not initialized:
        log.error("❌ MT5 nije pokrenut. Proveri login/server/path.")
        print("❌ MT5 nije pokrenut. Proveri login/server/path.")
        return

    log.info("✅ MT5 povezan uspešno.")

    # Kreiraj AI bota i strategiju
    ai_bot = AIBot(settings)
    strategy = StrategyHandler(settings)

    # Analiza tržišta
    try:
        rezultati = ai_bot.analyze_market()
    except Exception as e:
        log.error(f"❌ Greška tokom AI analize: {str(e)}")
        shutdown_mt5()
        return

    # Obrada rezultata
    for symbol, rezultat in rezultati.items():
        odluka = strategy.filter_action(
            rezultat["decision"],
            current_open_count=0  # za test
        )
        print(f"▶ {symbol}: {rezultat['decision']} → Finalna odluka: {odluka} | Score: {rezultat['score']:.2f}")

    # ✔ Automatski generiši izveštaje
    try:
        today = datetime.now()
        output_format = settings.get("report_output_format", "both")

        generate_single_report("daily", output_format=output_format)

        if today.weekday() == 6:  # Nedelja
            generate_single_report("weekly", output_format=output_format)

        if today.day == 1:  # Prvi dan u mesecu
            generate_single_report("monthly", output_format=output_format)

        if today.month == 12 and today.day == 31:
            generate_single_report("yearly", output_format=output_format)

    except Exception as e:
        log.warning(f"⚠️ Nije moguće generisati izveštaje: {e}")

    # Shutdown MT5
    shutdown_mt5()
    log.info("🛑 MT5 sesija zatvorena.")
    print("✅ Bot test završen.")

if __name__ == "__main__":
    main()
