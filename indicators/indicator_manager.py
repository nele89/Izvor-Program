# indicators/indicator_manager.py

import MetaTrader5 as mt5
import pandas as pd
import time
from indicators.indicator_utils import calculate_all_indicators
from utils.settings_handler import load_settings
from logs.logger import log

class IndicatorManager:
    def __init__(self, settings):
        self.settings = settings
        self.symbols = settings.get("pairs", ["XAUUSD"])
        self.timeframe = settings.get("timeframe", "M5")
        self.indicator_list = settings.get("indicators_list", ["RSI", "MACD", "MA50", "MA200", "ATR", "Supertrend"])
        self.enabled = settings.get("enable_indicators_engine", "yes") == "yes"

    def get_indicator_data(self, symbol, bars=100):
        """Učitava podatke za simbol i izračunava indikatore"""
        if not self.enabled:
            log.debug(f"⚠️ Indicator engine is disabled. Preskačem {symbol}")
            return None

        start_time = time.time()

        timeframe_enum = getattr(mt5, self.timeframe, mt5.TIMEFRAME_M5)
        if not mt5.symbol_select(symbol, True):
            log.warning(f"❌ Simbol '{symbol}' ne može da se selektuje.")
            return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe_enum, 0, bars)
        if rates is None or len(rates) == 0:
            log.warning(f"⚠️ Nema podataka za {symbol}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        try:
            indicators = calculate_all_indicators(df, self.indicator_list)
        except Exception as e:
            log.error(f"❌ Greška prilikom računanja indikatora za {symbol}: {e}")
            return None

        elapsed = time.time() - start_time
        log.info(f"📊 Indikatori za {symbol} obrađeni za {elapsed:.2f} sekundi.")
        return indicators

    def get_all_symbols_data(self):
        """Računa indikatore za sve simbole"""
        result = {}
        for symbol in self.symbols:
            data = self.get_indicator_data(symbol)
            if data is not None:
                result[symbol] = data
        return result
