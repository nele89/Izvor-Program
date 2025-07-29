# engine/ai_engine.py

from indicators.indicator_manager import IndicatorManager
from indicators.advanced_logic import evaluate_advanced_signals
from utils.settings_handler import load_settings
from logs.logger import log

from ml.experience_memory import DecisionMemory  # novo za trening

class AIBot:
    def __init__(self, settings):
        self.settings = settings
        self.indicator_engine = IndicatorManager(settings)
        self.ai_mode = settings.get("use_ml_model", "no") == "yes"
        self.memory_enabled = settings.get("ai_use_decision_memory", "yes") == "yes"
        self.memory = DecisionMemory(settings) if self.memory_enabled else None

    def analyze_market(self):
        """Glavna funkcija koja kombinuje indikatore i pravi AI odluku"""
        symbol_data = self.indicator_engine.get_all_symbols_data()
        decision_results = {}

        for symbol, df in symbol_data.items():
            advanced = evaluate_advanced_signals(df)
            score = advanced["signal_score"]

            action = "WAIT"
            if score >= 70:
                action = "BUY"
            elif score <= 30:
                action = "SELL"

            decision_results[symbol] = {
                "score": score,
                "decision": action,
                "golden_cross": advanced["golden_cross"],
                "death_cross": advanced["death_cross"],
                "rsi_divergence": advanced["rsi_divergence"]
            }

            log.info(f"[{symbol}] SCORE: {score} → ACTION: {action}")

            # Ako memorija uključena, zabeleži odluku
            if self.memory:
                self.memory.record(symbol, df, score, action)

        return decision_results
