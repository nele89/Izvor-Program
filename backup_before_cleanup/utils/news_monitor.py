import time
import threading
from datetime import datetime
from logs.logger import log
from utils.news_state import set_sentiment_state
from utils.news_fetcher import fetch_news  # Mora vraćati listu naslova ili dict-ova sa naslovima
from utils.sentiment_analyzer import analyze_sentiment  # Mora vraćati "positive", "neutral", "panic", "fear", "ignore"
from utils.settings_handler import load_settings

CURRENT_STATE = "neutral"

def _extract_headline_text(item):
    """Ekstraktuje naslov iz dict-a ili vrati string kakav god da je item."""
    if isinstance(item, dict):
        return (
            item.get("title") or
            item.get("headline") or
            item.get("summary") or
            str(item)
        )
    return str(item)

def is_within_trading_hours(start_hour, end_hour):
    now = datetime.now().time()
    start = datetime.strptime(start_hour, "%H:%M").time()
    end = datetime.strptime(end_hour, "%H:%M").time()
    # Podrška za preklapanje ponoći
    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end

def news_monitor_loop():
    global CURRENT_STATE
    settings = load_settings()
    start_hour = settings.get("start_hour", "08:00")
    end_hour = settings.get("end_hour", "22:00")
    interval_min = int(settings.get("check_interval_minutes", 15))
    interval_sec = max(60, interval_min * 60)  # Najmanje 60 sekundi, default 15 min

    while True:
        try:
            if not is_within_trading_hours(start_hour, end_hour):
                log.info("🕒 Van radnog vremena – preskačem proveru vesti.")
                time.sleep(interval_sec)
                continue

            headlines_raw = fetch_news()
            if not headlines_raw:
                log.warning("⚠️ Nema vesti za analizu.")
                set_sentiment_state("neutral")
                CURRENT_STATE = "neutral"
            else:
                # Izvuci čist tekst (title) iz svakog itema
                headlines = []
                for item in headlines_raw:
                    text = _extract_headline_text(item)
                    if text and len(text.strip()) > 3:
                        headlines.append(text.strip())
                if not headlines:
                    log.warning("⚠️ Nema validnih naslova za analizu.")
                    set_sentiment_state("neutral")
                    CURRENT_STATE = "neutral"
                else:
                    sentiment = analyze_sentiment(headlines)
                    set_sentiment_state(sentiment)
                    CURRENT_STATE = sentiment
                    log.info(f"🧠 Sentiment iz vesti: {sentiment.upper()}")

        except Exception as e:
            log.error(f"❌ Greška u news monitoru: {e}")
            set_sentiment_state("neutral")
            CURRENT_STATE = "neutral"

        time.sleep(interval_sec)

def get_current_sentiment():
    return CURRENT_STATE

def start_news_monitor():
    thread = threading.Thread(target=news_monitor_loop, daemon=True)
    thread.start()
