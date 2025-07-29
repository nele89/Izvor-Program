import configparser
import os

CONFIG_PATH = os.path.join("config", "config.ini")
NEWS_API_SECTION = "NEWS_API"
API_KEYS = ["primary", "secondary", "tertiary", "quaternary", "quinary"]

def ensure_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(f"[{NEWS_API_SECTION}]\n")
            for k in API_KEYS:
                f.write(f"{k} = \n")

def load_news_api_keys():
    ensure_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    if not config.has_section(NEWS_API_SECTION):
        config.add_section(NEWS_API_SECTION)
    return {k: config.get(NEWS_API_SECTION, k, fallback="") for k in API_KEYS}

def save_news_api_keys(keys_dict):
    ensure_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    if not config.has_section(NEWS_API_SECTION):
        config.add_section(NEWS_API_SECTION)
    for k in API_KEYS:
        config.set(NEWS_API_SECTION, k, keys_dict.get(k, ""))
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)

def set_api_key(position, value):
    """position: 1-5, value: string"""
    if 1 <= position <= 5:
        keys = load_news_api_keys()
        keys[API_KEYS[position-1]] = value
        save_news_api_keys(keys)
        print(f"✅ Sačuvan ključ {API_KEYS[position-1]} = {value}")
    else:
        print("❌ Pozicija mora biti od 1 do 5.")

def get_api_keys():
    """Vrati sve API ključeve kao dict."""
    return load_news_api_keys()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # Ispiši sve ključeve
        keys = get_api_keys()
        print("NEWS API keys:")
        for k, v in keys.items():
            print(f"  {k}: {v}")
    elif len(sys.argv) == 3 and sys.argv[1].isdigit():
        pos = int(sys.argv[1])
        val = sys.argv[2]
        set_api_key(pos, val)
    else:
        print("Usage:")
        print("  python news_api_key_manager.py           # ispis svih ključeva")
        print("  python news_api_key_manager.py 2 moj_kljuc12345")
