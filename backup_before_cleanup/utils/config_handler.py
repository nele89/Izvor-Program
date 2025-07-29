import configparser
import os
from logs.logger import log

CONFIG_PATH = "config/config.ini"

def get_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        log.error("❌ config.ini ne postoji.")
        return None
    config.read(CONFIG_PATH)
    return config

def get_news_api_keys():
    config = get_config()
    if config is None:
        return []
    if config.has_section("NEWS_API") and config.has_option("NEWS_API", "keys"):
        keys = config.get("NEWS_API", "keys").split(",")
        return [k.strip() for k in keys if k.strip()]
    return []

def save_news_api_keys(keys):
    config = get_config()
    if config is None:
        config = configparser.ConfigParser()

    if not config.has_section("NEWS_API"):
        config.add_section("NEWS_API")

    key_string = ", ".join(keys)
    config.set("NEWS_API", "keys", key_string)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)

    log.info("✅ News API ključevi uspešno sačuvani.")
