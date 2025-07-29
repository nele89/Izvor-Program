# engine/news_filter.py

import random
import time
from logs.logger import log

class NewsFilter:
    def __init__(self, settings):
        self.settings = settings
        self.last_check_time = 0
        self.check_interval_sec = int(settings.get("news_check_interval", 600))  # default 10 min
        self.active = True  # koristi se za buduću GUI lampicu

    def should_check_news(self):
        now = time.time()
        return (now - self.last_check_time) > self.check_interval_sec

    def check_news(self):
        if not self.active:
            return False

        if not self.should_check_news():
            return False

        self.last_check_time = time.time()

        # 👇 Ovde bi bio pravi API poziv – privremeno simuliramo
        risk_news = random.choice([True, False, False, False])  # 25% šanse za rizičnu vest

        if risk_news:
            log.warning("📰 Detektovana rizična vest! Trgovanje se pauzira.")
            return True
        else:
            log.info("📰 Vesti proverene – nema rizika.")
            return False
