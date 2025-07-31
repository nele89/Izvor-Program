# ai/gold_trade.py

import traceback
from utils.logger import log_change
from ai.trading_engine import TradingEngine

class GoldTrade:
    """Klasa za trgovanje zlatom (XAU/USD) sa osnovnom zaštitom i logovanjem."""

    def __init__(self, max_lot: float = 10.0, symbol: str = "XAUUSD"):
        """
        :param max_lot: Maksimalna veličina lota za sigurnost
        :param symbol: Simbol za trgovanje, default XAU/USD
        """
        self.symbol = symbol
        self.max_lot = max_lot
        self.trading_engine = TradingEngine()

    def execute_trade(self, direction: str, lot_size: float, stop_loss: float = None, take_profit: float = None):
        """
        Izvršava trejd sa proverama i logovanjem.
        :param direction: 'buy' ili 'sell'
        :param lot_size: Veličina lota
        :param stop_loss: Opcioni SL
        :param take_profit: Opcioni TP
        """
        if lot_size > self.max_lot:
            log_change(f"[GOLD_TRADE] ⚠️ Lot {lot_size} je veći od dozvoljenog maksimuma {self.max_lot}. Trejd odbijen.")
            return False

        log_change(f"[GOLD_TRADE] ▶️ Pokušaj trejda {direction.upper()} {lot_size} lot na {self.symbol}...")

        try:
            result = self.trading_engine.place_order(
                symbol=self.symbol,
                direction=direction,
                lot=lot_size,
                sl=stop_loss,
                tp=take_profit
            )
            if result:
                log_change(f"[GOLD_TRADE] ✅ Trejd uspešno izvršen: {direction.upper()} {lot_size} lot na {self.symbol}")
            else:
                log_change(f"[GOLD_TRADE] ❌ MT5 nije prihvatio trejd za {self.symbol}")
            return result
        except Exception as e:
            log_change(f"[GOLD_TRADE] ❌ Greška pri izvršavanju trejda: {e}")
            log_change(traceback.format_exc())
            return False


# Debug test
if __name__ == "__main__":
    gt = GoldTrade(max_lot=5.0)
    # Test BUY
    success = gt.execute_trade("buy", 0.1, stop_loss=1920.0, take_profit=1940.0)
    print("Rezultat BUY:", success)
    # Test SELL
    success = gt.execute_trade("sell", 0.2)
    print("Rezultat SELL:", success)
