# engine/strategy_handler.py

from datetime import datetime
from utils.settings_handler import load_settings
from logs.logger import log

class StrategyHandler:
    def __init__(self, settings):
        self.settings = settings

    def is_trading_allowed_now(self):
        if self.settings.get("auto_trading", "off") != "on":
            log.debug("📴 Auto trading is off.")
            return False

        now = datetime.now().time()
        start = datetime.strptime(self.settings["start_hour"], "%H:%M").time()
        end = datetime.strptime(self.settings["end_hour"], "%H:%M").time()

        if start <= now <= end:
            return True
        else:
            log.debug(f"⏰ Van vremena trgovanja: {now}")
            return False

    def can_open_more_positions(self, current_open_count, scalping=False):
        if scalping:
            max_scalping = int(self.settings.get("max_scalping_positions", 5))
            if current_open_count < max_scalping:
                return True
            else:
                log.debug(f"⚠️ Prekoračen broj skalping pozicija: {current_open_count}/{max_scalping}")
                return False
        else:
            max_open = int(self.settings.get("max_open_positions", 10))
            if current_open_count < max_open:
                return True
            else:
                log.debug(f"⚠️ Prekoračen broj pozicija: {current_open_count}/{max_open}")
                return False

    def filter_action(self, ai_decision, current_open_count):
        """
        Finalna odluka da li se AI signal može primeniti
        """
        if not self.is_trading_allowed_now():
            return "WAIT"

        scalping_mode = self.settings.get("scalping_mode", "no") == "yes"
        if not self.can_open_more_positions(current_open_count, scalping=scalping_mode):
            return "WAIT"

        return ai_decision  # može biti BUY, SELL, WAIT
