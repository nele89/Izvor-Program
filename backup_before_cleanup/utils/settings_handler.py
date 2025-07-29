import configparser
import os
import shutil
import sys
import json
from logs.logger import log
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CONFIG_PATH = os.path.join("config", "config.ini")
BACKUP_PATH = os.path.join("config", "config_backup.ini")
JSON_PATH = os.path.join("config", "settings.json")

def ensure_dirs():
    for p in [os.path.dirname(CONFIG_PATH), os.path.dirname(JSON_PATH)]:
        os.makedirs(p, exist_ok=True)

def validate_required_keys(config):
    required_structure = {
        "MT5": ["login", "password", "server", "path"],
        "TRADING": ["symbol", "lot", "timeframe", "auto_trading", "start_hour", "end_hour", "mode"],
        "PAIR_LIST": ["pairs"],
        "UI": ["theme", "show_alerts", "language"],
        "REPORTING": ["generate_daily", "generate_weekly", "generate_monthly", "generate_yearly", "report_output_format"],
        "ADVANCED": [
            "auto_start_by_market_hours", "ai_adjusts_indicators", "use_ml_model",
            "enable_indicators_engine", "indicators_list", "indicators_strategy_mode",
            "ai_training_frequency", "ai_use_decision_memory", "ai_training_last_n",
            "ai_max_candles", "restart_mt5_on_crash", "live_gui_refresh_seconds",
            "allow_user_override_ai_indicators"
        ],
        "NEWS_API": ["primary", "secondary", "tertiary", "quaternary", "quinary"]
    }

    for section, keys in required_structure.items():
        if not config.has_section(section):
            raise ValueError(f"❌ Nedostaje sekcija: [{section}] u config.ini")
        for key in keys:
            if not config.has_option(section, key):
                raise ValueError(f"❌ Nedostaje ključ '{key}' u sekciji [{section}]")

def load_ini_config():
    try:
        config = configparser.ConfigParser()
        if not os.path.exists(CONFIG_PATH) and os.path.exists(BACKUP_PATH):
            shutil.copy(BACKUP_PATH, CONFIG_PATH)
            log.warning("⚠️ config.ini nije pronađen, koristi se backup fajl.")
        if os.path.exists(CONFIG_PATH):
            config.read(CONFIG_PATH, encoding="utf-8")
            validate_required_keys(config)
            return config
        else:
            log.warning(f"⚠️ INI fajl ne postoji: {CONFIG_PATH}")
            return None
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju config.ini: {e}")
        return None

def load_settings(filename=CONFIG_PATH):
    ensure_dirs()
    config = configparser.ConfigParser()

    if not os.path.exists(filename) and os.path.exists(BACKUP_PATH):
        shutil.copy(BACKUP_PATH, filename)
        log.warning("⚠️ config.ini nije pronađen, koristi se backup fajl.")

    settings = {}

    try:
        with open(filename, encoding="utf-8") as f:
            config.read_file(f)

        validate_required_keys(config)

        for section in config.sections():
            for key in config[section]:
                settings[key] = config.get(section, key)

        # 'mode' iz INI (sekcija TRADING)
        if config.has_option("TRADING", "mode"):
            ini_mode = config.get("TRADING", "mode").strip().lower()
            if ini_mode in ("scalping", "daily"):
                settings["mode"] = ini_mode
            else:
                log.warning(f"⚠️ Nevalidan TRADING.mode u config.ini: '{ini_mode}', koristi se 'scalping'.")
                settings["mode"] = "scalping"
        else:
            settings["mode"] = "scalping"

        # Pretvaranje određenih vrednosti u liste
        settings["pairs"] = [
            s.strip() for s in config.get("PAIR_LIST", "pairs", fallback="XAUUSD").split(",") if s.strip()
        ]
        settings["indicators_list"] = [
            s.strip() for s in config.get("ADVANCED", "indicators_list", fallback="RSI,MACD").split(",") if s.strip()
        ]

        # NEWS_API ključevi
        settings["news_apis"] = {
            "primary":   config.get("NEWS_API", "primary", fallback=""),
            "secondary": config.get("NEWS_API", "secondary", fallback=""),
            "tertiary":  config.get("NEWS_API", "tertiary", fallback=""),
            "quaternary":config.get("NEWS_API", "quaternary", fallback=""),
            "quinary":   config.get("NEWS_API", "quinary", fallback="")
        }

        # NEWS_FILTER ključne reči (ako postoji sekcija)
        if config.has_section("NEWS_FILTER") and config.has_option("NEWS_FILTER", "keywords"):
            settings["news_keywords"] = [
                k.strip() for k in config.get("NEWS_FILTER", "keywords", fallback="").split(",") if k.strip()
            ]

        # Override iz .env ako postoje param_env reference
        for param in ["login", "password", "server", "path"]:
            env_key = settings.get(f"{param}_env", "").strip()
            if env_key:
                env_val = os.getenv(env_key)
                if env_val:
                    settings[param] = env_val

        # Override vrednosti iz settings.json
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as jf:
                try:
                    json_data = json.load(jf)
                    if isinstance(json_data, dict):
                        settings.update(json_data)
                        if "mode" in json_data and json_data["mode"].strip().lower() in ("scalping", "daily"):
                            settings["mode"] = json_data["mode"].strip().lower()
                except Exception as je:
                    log.warning(f"⚠️ Greška u JSON settings: {je}")

        # Default news_keywords ako nije postavljeno
        if "news_keywords" not in settings or not settings["news_keywords"]:
            settings["news_keywords"] = [
                "gold", "XAUUSD", "USD", "GLD", "inflation", "FED", "precious metals", "central bank",
                "interest rate", "FOMC", "jobs report", "CPI", "GDP", "treasury", "rate hike",
                "yield", "safe haven", "geopolitical"
            ]

        # Parsiranje history_start_date ili default
        hsd = settings.get("history_start_date")
        if isinstance(hsd, str):
            try:
                settings["history_start_date"] = datetime.fromisoformat(hsd)
            except Exception:
                log.warning(f"⚠️ Nevalidan history_start_date: {hsd}, koristi se default 2021-07-11.")
                settings["history_start_date"] = datetime(2021, 7, 11)
        else:
            settings["history_start_date"] = datetime(2021, 7, 11)

        log.info(f"✅ Podešavanja uspešno učitana (MODE: {settings['mode']})")

    except Exception as e:
        log.error(f"❌ Greška prilikom učitavanja podešavanja: {e}")
        sys.exit(1)

    return settings

def save_settings(settings, json_path=JSON_PATH):
    """
    Snima podešavanja u JSON fajl.
    """
    ensure_dirs()
    try:
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(settings, jf, indent=2, ensure_ascii=False)
        log.info(f"✅ Podešavanja uspešno snimljena u {json_path}")
        return True
    except Exception as e:
        log.error(f"❌ Greška prilikom snimanja podešavanja: {e}")
        return False

if __name__ == "__main__":
    settings = load_settings()
    print("\n✅ Test učitavanja završen. Primer podešavanja:\n")
    print(json.dumps(settings, indent=4, ensure_ascii=False))
    save_settings(settings)
