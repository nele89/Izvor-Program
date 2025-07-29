import threading

class NewsState:
    """
    Centralizovano upravlja statusom vesti i signalom za pauzu trgovanja.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.status = "neutral"  # panic, fear, neutral, positive, ignore
        self.pause_due_to_news = False

    def set_status(self, new_status):
        with self._lock:
            self.status = new_status
            # Samo panic/fear pauziraju trgovanje
            self.pause_due_to_news = new_status in ("panic", "fear")

    def get_status(self):
        with self._lock:
            return self.status

    def should_pause_trading(self):
        with self._lock:
            return self.pause_due_to_news

    def reset_pause(self):
        with self._lock:
            self.pause_due_to_news = False

# Singleton
news_state = NewsState()

# === API za ostatak programa ===

def set_sentiment_state(state: str):
    news_state.set_status(state)
    # Resetuj pauzu ako vest više nije panic/fear
    if state not in ("panic", "fear"):
        news_state.reset_pause()

def get_sentiment_state() -> str:
    return news_state.get_status()

def set_news_pause_state(pause: bool):
    with news_state._lock:
        news_state.pause_due_to_news = pause

def get_news_pause_state() -> bool:
    return news_state.should_pause_trading()

def get_latest_sentiment() -> str:
    return news_state.get_status()

get_news_pause_status = get_news_pause_state

def reset_news_pause():
    news_state.reset_pause()

# ----------- NOVI DEO: analizator relevantnosti i sentimenta -----------

def is_news_relevant(news_title: str, news_summary: str, keywords: list) -> bool:
    """
    Vraća True ako bar jedna ključna reč postoji u naslovu ili summary-ju vesti.
    """
    text = (news_title + " " + news_summary).lower()
    return any(kw.lower() in text for kw in keywords)

def analyze_and_update_sentiment(news_title: str, news_summary: str = "", keywords: list = None) -> str:
    """
    Analizira sentiment i ažurira stanje SAMO AKO JE VEST RELEVANTNA!
    Ako nije relevantna, status ide na 'ignore' (ne blokira program).
    """
    # Učitaj podrazumevane ključne reči iz settings, ako nisu prosleđene
    if keywords is None:
        try:
            from utils.settings_handler import load_settings
            keywords = load_settings().get("news_keywords", [])
        except Exception:
            keywords = []

    if not keywords or not is_news_relevant(news_title, news_summary, keywords):
        news_state.set_status("ignore")
        news_state.reset_pause()
        return "ignore"

    # Sentiment analiza ključnih reči
    text = (news_title + " " + news_summary).lower()

    panic_keywords = ["crash", "collapse", "panic", "recession", "depression"]
    fear_keywords = ["inflation", "interest rate", "war", "uncertainty", "volatile"]
    positive_keywords = ["growth", "recovery", "bull", "optimism", "rally"]

    if any(kw in text for kw in panic_keywords):
        news_state.set_status("panic")
        return "panic"
    elif any(kw in text for kw in fear_keywords):
        news_state.set_status("fear")
        return "fear"
    elif any(kw in text for kw in positive_keywords):
        news_state.set_status("positive")
        news_state.reset_pause()
        return "positive"
    else:
        news_state.set_status("neutral")
        news_state.reset_pause()
        return "neutral"
