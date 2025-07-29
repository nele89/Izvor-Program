import threading
import time
from logs.logger import log
from utils.program_state import is_program_running, set_running_state
from utils.settings_handler import load_settings

class TradingHandler:
    def __init__(self):
        self.settings = load_settings()
        self.trading_thread = None
        self.running = False
        log.info("🔄 TradingHandler inicijalizovan.")

    def start_trading(self):
        if self.running:
            log.warning("⏳ Trading je već aktivan.")
            return
        self.running = True
        set_running_state(True)
        self.trading_thread = threading.Thread(target=self._trading_loop, name="TradingThread", daemon=True)
        self.trading_thread.start()
        log.info("▶️ Pokrenuto pravo trejdovanje.")

    def stop_trading(self):
        if not self.running:
            log.warning("⏹️ Trading nije bio aktivan.")
            return
        self.running = False
        set_running_state(False)
        log.info("⏹️ Trading zaustavljen. Čekam da se thread završi...")
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=10)
        log.info("✅ Trading thread završen.")

    def is_trading_active(self):
        return self.running and is_program_running()

    def _trading_loop(self):
        log.info("♻️ Trading loop startovan.")
        while self.running and is_program_running():
            # TODO: Ovde ide glavna logika trejdovanja, AI pozivi, otvaranje/zatvaranje pozicija...
            self.check_and_trade()
            time.sleep(float(self.settings.get("live_gui_refresh_seconds", 5)))
        log.info("💤 Trading loop izašao.")

    def check_and_trade(self):
        # TODO: Ubaci AI ili strategiju za signal/odluku, proveri uslove, pozovi trade funkciju itd.
        # Primer (stub logika):
        log.debug("📊 (Stub) Provera signala za trgovanje...") 
        # self.open_position() / self.close_position() - po potrebi

    def open_position(self, symbol=None, lot=None, **kwargs):
        # TODO: Logika za otvaranje pozicije (API ili simulacija)
        symbol = symbol or self.settings.get("symbol", "XAUUSD")
        lot = lot or self.settings.get("lot", 0.01)
        log.info(f"🟢 Otvaram poziciju: {symbol}, lot: {lot}")
        # Implementiraj API/MT5 poziv ovde

    def close_position(self, position_id=None, **kwargs):
        # TODO: Logika za zatvaranje pozicije
        log.info(f"🔴 Zatvaram poziciju: {position_id}")
        # Implementiraj API/MT5 zatvaranje ovde

# Primer pokretanja/tradanja direktno iz fajla:
if __name__ == "__main__":
    th = TradingHandler()
    th.start_trading()
    time.sleep(15)  # Radi 15 sekundi
    th.stop_trading()
