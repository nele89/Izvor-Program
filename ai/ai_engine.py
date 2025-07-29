import random
from logs.logger import log


class AIEngine:
    def __init__(self, settings):
        self.settings = settings
        self.training_data = []
        self.prediction = {}

    def update_data(self, candles):
        self.training_data = candles[-int(self.settings.get("ai_max_candles", 1000)):]
        log.info(f"📈 AI podaci ažurirani sa {len(self.training_data)} svećica")

    def train(self):
        if not self.training_data:
            log.warning("⚠️ Nema podataka za treniranje AI modela")
            return
        # Simulacija treniranja
        log.info("🧠 Treniranje AI modela na osnovu svećica...")

    def predict(self, symbol):
        # Lažna predikcija radi testiranja
        signal = random.choice(["buy", "sell", "hold"])
        self.prediction[symbol] = signal
        log.info(f"🤖 AI predikcija za {symbol}: {signal.upper()}")
        return signal

    def get_prediction(self, symbol):
        return self.prediction.get(symbol, "hold")

    def should_train_now(self, counter):
        interval = int(self.settings.get("ai_training_frequency", 100))
        return counter % interval == 0
