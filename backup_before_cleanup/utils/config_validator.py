# 📁 Lokacija: utils/validate_config.py

import configparser
import os
from dotenv import load_dotenv
from logs.logger import log

CONFIG_PATH = "config/config.ini"
ENV_PATH = ".env"

# 📌 Obavezna podešavanja po sekcijama
REQUIRED_KEYS = {
    "MT5": ["path", "login", "password", "server"],
    "TRADING": ["symbol", "lot", "timeframe", "start_hour", "end_hour", "tp_sl_strategy"],
    "PAIR_LIST": ["pairs"],
    "REPORTING": ["generate_daily", "generate_weekly", "generate_monthly", "generate_yearly", "report_output_format"],
    "UI": ["ui_theme"],
    "ADVANCED": ["ai_training_frequency", "ai_training_last_n"]
}

# 📌 Obavezne .env promenljive
REQUIRED_ENV_VARS = [
    "MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER", "MT5_PATH",
    "NEWS_API_KEY"
]


def validate_config():
    success = True

    # ✅ Provera config.ini
    if not os.path.exists(CONFIG_PATH):
        log.error("❌ config.ini fajl ne postoji.")
        print("⚠️ Nema config.ini fajla – kreiraj ga ili kopiraj primer.")
        return False

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    for section, keys in REQUIRED_KEYS.items():
        if not config.has_section(section):
            log.error(f"❌ Nedostaje sekcija: [{section}]")
            print(f"⛔ Dodaj sekciju [{section}] u config.ini")
            success = False
            continue

        for key in keys:
            value = config[section].get(key, "").strip()
            if not value:
                log.error(f"⚠️ Nedostaje ključ '{key}' u sekciji [{section}]")
                print(f"🔧 Dodaj ključ '{key}' u sekciju [{section}]")
                success = False

    # ✅ Provera .env fajla
    if not os.path.exists(ENV_PATH):
        log.error("❌ .env fajl ne postoji.")
        print("⚠️ Nema .env fajla – kreiraj ga i ubaci osnovne promenljive.")
        success = False
    else:
        load_dotenv()
        for var in REQUIRED_ENV_VARS:
            if not os.getenv(var):
                log.error(f"⚠️ Nedostaje promenljiva '{var}' u .env fajlu.")
                print(f"🔧 Dodaj u .env: {var}=... ")
                success = False

    if success:
        log.info("✅ config.ini i .env validacija uspešna.")
        print("✅ Sve postavke su ispravne.")
    else:
        log.warning("⚠️ Detektovane greške u config.ini ili .env – proveri iznad.")
        print("⚠️ Program neće raditi dok se sve ne popravi.")

    return success


# Test opcija (ako želiš da testiraš direktno ovaj fajl)
if __name__ == "__main__":
    validate_config()
