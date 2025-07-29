import time
from threading import Thread
from utils.settings_handler import load_settings
from logs.logger import log

class NewsHandler:
    def __init__(self):
        self.settings = load_settings()
        self.api_keys = self.settings.get("news_apis", {})
        self.check_interval = int(self.settings.get("news_check_interval", 600))  # default 10 minuta
        self.active_sources = [
            key for key, active in self.api_keys.items() if active and self.api_keys[key]
        ]
        self.news_negative = False
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.run, daemon=True)
            self.thread.start()
            log.info("📰 NewsHandler pokrenut.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("🛑 NewsHandler zaustavljen.")

    def run(self):
        while self.running:
            self.analyze_news()
            time.sleep(self.check_interval)

    def analyze_news(self):
        # Simulacija AI procene: u realnom slučaju bi se ovde pozivao API i slao sadržaj u AI model
        try:
            log.info("📡 Analiziram vesti sa aktivnih izvora...")
            for source in self.active_sources:
                # Simuliramo jednu od vrednosti da je loša vest
                if "war" in source.lower() or "crisis" in source.lower():
                    self.news_negative = True
                    log.warning(f"⚠️ Detektovane negativne vesti iz {source}")
                    return
            self.news_negative = False
            log.info("✅ Nema negativnih vesti trenutno.")
        except Exception as e:
            log.error(f"❌ Greška tokom analize vesti: {e}")

    def is_negative(self):
        return self.news_negative
