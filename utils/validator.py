import os
import configparser
from logs.logger import log
from dotenv import load_dotenv

CONFIG_PATH = "config/config.ini"

def validate_config():
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_PATH):
        raise Exception(f"❌ config.ini fajl ne postoji na lokaciji: {CONFIG_PATH}")

    config.read(CONFIG_PATH, encoding="utf-8")

    required_sections = ["MT5", "TRADING", "UI", "PAIR_LIST", "REPORTING", "ADVANCED"]
    for section in required_sections:
        if section not in config:
            raise Exception(f"❌ Nedostaje sekcija: [{section}] u config.ini")

    mt5 = config["MT5"]
    for key in ["login", "password", "server", "path"]:
        if not mt5.get(key):
            raise Exception(f"❌ MT5 podešavanje '{key}' nedostaje u config.ini")

    log.info("✅ config.ini validan.")


def validate_env():
    dotenv_path = ".env"

    if not os.path.exists(dotenv_path):
        raise Exception("❌ .env fajl nije pronađen!")

    load_dotenv(dotenv_path)

    required_vars = ["MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER", "MT5_PATH"]

    for var in required_vars:
        if not os.getenv(var):
            raise Exception(f"❌ Nedostaje promenljiva okruženja: {var}")

    log.info("✅ .env fajl validan.")
