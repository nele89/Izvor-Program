# mt5/mt5_monitor.py

import os
import time
import subprocess
from logs.logger import log
from utils.settings_handler import load_settings
from mt5.data_collector import is_mt5_connected, initialize_mt5

def monitor_and_restart_mt5():
    settings = load_settings()
    restart_enabled = settings.get("restart_mt5_on_crash", "yes") == "yes"
    mt5_path = settings.get("path", "")

    if not restart_enabled:
        log.info("🛑 Automatski restart MT5 je onemogućen u podešavanjima.")
        return

    if is_mt5_connected():
        log.debug("✅ MT5 terminal radi normalno.")
        return

    log.warning("⚠️ MT5 nije povezan. Pokušaj restarta...")

    try:
        if os.path.exists(mt5_path):
            subprocess.Popen(mt5_path)
            log.info("🔁 MT5 terminal pokrenut ponovo.")
            time.sleep(5)  # čekaj da se digne
            if not initialize_mt5(
                path=mt5_path,
                login=int(settings.get("login")),
                password=settings.get("password"),
                server=settings.get("server")
            ):
                log.error("❌ MT5 restart nije uspeo.")
            else:
                log.info("✅ MT5 ponovo uspešno povezan.")
        else:
            log.error(f"❌ Putanja do MT5 terminala nije validna: {mt5_path}")
    except Exception as e:
        log.error(f"❌ Greška pri pokušaju restarta MT5: {e}")
