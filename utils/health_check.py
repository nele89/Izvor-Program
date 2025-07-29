import os
import MetaTrader5 as mt5
from logs.logger import log

def check_mt5_connection(settings):
    path = settings.get("path")
    login = settings.get("login")
    password = settings.get("password")
    server = settings.get("server")

    if not os.path.exists(path):
        return False, f"❌ Ne postoji putanja do MetaTrader 5: {path}"

    if not mt5.initialize(path, login=int(login), password=password, server=server):
        return False, f"❌ Neuspešna konekcija sa MT5: {mt5.last_error()}"

    account_info = mt5.account_info()
    if account_info is None:
        return False, "❌ Ne mogu da dobijem podatke o nalogu iz MT5."

    return True, f"✅ MT5 konekcija uspešna: {account_info.name}"

def check_symbol_validity(symbol):
    if not mt5.symbol_select(symbol, True):
        return False, f"❌ Simbol nije validan ili nije omogućeno trgovanje: {symbol}"
    return True, f"✅ Simbol {symbol} je validan."

def run_health_check(settings):
    messages = []

    ok, msg = check_mt5_connection(settings)
    messages.append(msg)
    if not ok:
        return False, messages

    symbol = settings.get("symbol", "XAUUSD")
    ok, msg = check_symbol_validity(symbol)
    messages.append(msg)

    return ok, messages
