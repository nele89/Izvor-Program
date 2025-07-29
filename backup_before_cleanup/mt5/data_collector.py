# mt5/data_collector.py

import MetaTrader5 as mt5
import pandas as pd
from logs.logger import log


def initialize_mt5(path=None, login=None, password=None, server=None):
    if not mt5.initialize(path, login=login, password=password, server=server):
        log.error(f"❌ Neuspešna MT5 inicijalizacija: {mt5.last_error()}")
        return False

    # Provera konekcije
    account_info = mt5.account_info()
    if account_info is None:
        log.error("❌ Neuspešno preuzimanje informacija o nalogu nakon inicijalizacije.")
        return False

    log.info(f"✅ MT5 uspešno inicijalizovan za nalog: {account_info.login}")
    return True


def shutdown_mt5():
    mt5.shutdown()
    log.info("🛑 MT5 shutdown završen")


def get_symbol_data(symbol, timeframe="M5", bars=100):
    tf = getattr(mt5, timeframe, mt5.TIMEFRAME_M5)

    if not mt5.symbol_select(symbol, True):
        log.warning(f"⚠️ Symbol '{symbol}' nije moguće selektovati ili ne postoji.")
        return None

    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)

    if rates is None or len(rates) == 0:
        log.warning(f"⚠️ Nema podataka za {symbol}")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df


def get_multiple_symbols(symbols, timeframe="M5", bars=100):
    data = {}
    for symbol in symbols:
        df = get_symbol_data(symbol, timeframe, bars)
        if df is not None:
            data[symbol] = df
        else:
            log.warning(f"❌ Neuspešno prikupljanje podataka za: {symbol}")
    return data


def is_mt5_connected():
    return mt5.terminal_info() is not None and mt5.version() is not None
