from datetime import datetime, timedelta
from logs.logger import log

class NewsPauseController:
    def __init__(self, check_interval_seconds=600):
        self.pause_due_to_news = False
        self.last_check_time = None
        self.interval = timedelta(seconds=check_interval_seconds)

    def should_check_news(self):
        now = datetime.now()
        if self.last_check_time is None or now - self.last_check_time >= self.interval:
            self.last_check_time = now
            return True
        return False

    def update_news_sentiment(self, sentiment_score):
        """
        sentiment_score: broj između -1 i 1
        npr: -0.8 = jako negativno, 0 = neutralno, 0.7 = pozitivno
        """
        if sentiment_score < -0.4:
            self.pause_due_to_news = True
            log.warning("🛑 Trgovanje pauzirano zbog negativnih vesti (sentiment_score < -0.4)")
        else:
            self.pause_due_to_news = False
            log.info("✅ Trgovanje dozvoljeno – sentiment neutralan ili pozitivan")

    def is_trading_allowed(self):
        return not self.pause_due_to_news
