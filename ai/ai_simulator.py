# ai/ai_simulator.py

import os
import traceback
from utils.logger import log_change
from ai.strategy_manager import StrategyManager
from ai.trading_engine import TradingEngine

class AISimulator:
    """Simulator za offline testiranje AI strategija."""

    def __init__(self, historical_data: list):
        """
        :param historical_data: Lista sa istorijskim podacima (OHLC + volume)
        """
        self.data = historical_data
        self.results = []
        self.strategy_manager = StrategyManager()
        self.trading_engine = TradingEngine(simulation_mode=True)

    def run_simulation(self):
        """Pokreće offline simulaciju na osnovu istorijskih podataka."""
        if not self.data or len(self.data) == 0:
            log_change("[AI_SIMULATOR] ⚠️ Nema dostupnih podataka za simulaciju.")
            return []

        log_change(f"[AI_SIMULATOR] ▶️ Pokrećem simulaciju sa {len(self.data)} podataka...")

        for i, candle in enumerate(self.data):
            try:
                # Validacija osnovnih polja
                if len(candle) < 5:
                    log_change(f"[AI_SIMULATOR] ⚠️ Preskačem red {i}, nedovoljno podataka: {candle}")
                    continue

                # Generiši signal kroz StrategyManager
                signal = self.strategy_manager.generate_signal(candle)

                # Simuliraj trejd kroz TradingEngine
                result = self.trading_engine.simulate_trade(signal, candle)
                self.results.append(result)

                if i % 100 == 0:  # periodični log
                    log_change(f"[AI_SIMULATOR] ℹ️ Obrada {i}/{len(self.data)} podataka...")

            except Exception as e:
                log_change(f"[AI_SIMULATOR] ❌ Greška u simulaciji na indeksu {i}: {e}")
                log_change(traceback.format_exc())
                # Ne prekidamo simulaciju, idemo dalje

        log_change(f"[AI_SIMULATOR] ✅ Simulacija završena. Ukupno trejdova: {len(self.results)}")
        return self.results

# Debug test
if __name__ == "__main__":
    dummy_data = [
        [1.2345, 1.2350, 1.2330, 1.2340, 1000],  # OHLCV primer
        [1.2340, 1.2360, 1.2335, 1.2355, 1200]
    ]
    sim = AISimulator(dummy_data)
    res = sim.run_simulation()
    print("Rezultati simulacije:", res)
