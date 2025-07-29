import MetaTrader5 as mt5
import subprocess
import os
import pandas as pd
from logs.logger import log
from utils.settings_handler import load_settings
import threading
import time

def connect_direct():
    s = load_settings()
    return connect_to_mt5(
        path=s.get("path"),
        login=int(s.get("login")),
        password=s.get("password"),
        server=s.get("server")
    )

def connect_to_mt5(path, login, password, server):
    if not mt5.initialize(path, login=login, password=password, server=server):
        log.error(f"❌ MT5 nije uspeo da se inicijalizuje: {mt5.last_error()}")
        return False
    log.info("✅ Uspešno konektovan na MetaTrader 5")
    return True

def disconnect_mt5():
    mt5.shutdown()
    log.info("🔌 Veza sa MT5 zatvorena.")

def check_mt5_connection():
    if not mt5.initialize():
        return False
    info = mt5.terminal_info()
    mt5.shutdown()
    return info is not None

def restart_mt5_terminal(mt5_path):
    try:
        log.warning("🔄 Restartujem MT5 terminal...")
        subprocess.Popen([mt5_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        return True
    except Exception as e:
        log.error(f"❌ Ne mogu da restartujem MT5: {e}")
        return False

def get_account_info():
    if not mt5.initialize():
        log.error("❌ MT5 nije inicijalizovan za get_account_info")
        return {}

    account_info = mt5.account_info()
    mt5.shutdown()

    if account_info is None:
        log.error("❌ Ne mogu da pročitam podatke o računu.")
        return {}

    return {
        "balance": account_info.balance,
        "equity": account_info.equity,
        "margin": account_info.margin,
        "margin_level": account_info.margin_level,
        "profit": account_info.profit,
        "currency": account_info.currency
    }

def get_open_positions(symbol=None):
    if not mt5.initialize():
        log.error("❌ MT5 nije inicijalizovan za get_open_positions")
        return []

    positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    mt5.shutdown()

    if positions is None:
        log.warning(f"⚠️ Nema otvorenih pozicija{f' za {symbol}' if symbol else ''}.")
        return []
    return positions

def close_all_positions(symbol=None):
    if not mt5.initialize():
        log.error("❌ MT5 nije inicijalizovan za close_all_positions")
        return

    positions = mt5.positions_get()
    if not positions:
        log.info("ℹ️ Nema pozicija za zatvaranje.")
        mt5.shutdown()
        return

    for pos in positions:
        if symbol and pos.symbol != symbol:
            continue

        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            log.error(f"❌ Ne mogu da dobijem cenu za {pos.symbol}")
            continue

        price = tick.bid if order_type == mt5.ORDER_TYPE_BUY else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": "Zatvori poziciju",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"✅ Pozicija za {pos.symbol} zatvorena")
        else:
            log.error(f"❌ Neuspeh zatvaranja pozicije za {pos.symbol}: {result.comment}")

    mt5.shutdown()

def open_trade(symbol, lot, order_type, tp=None, sl=None):
    if not mt5.initialize():
        log.error("❌ MT5 nije inicijalizovan za open_trade")
        return False

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log.error(f"❌ Ne mogu da dobijem cenu za {symbol}")
        mt5.shutdown()
        return False

    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Izvor trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    mt5.shutdown()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        log.error(f"❌ Greška pri slanju naloga: {result.retcode} - {result.comment}")
        return False

    log.info(f"📤 Nalog uspešno poslat: ticket #{result.order}")
    return True

def get_symbol_data(symbol, timeframe="M5", bars=100):
    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }

    if not mt5.initialize():
        log.error("❌ Nije moguće inicijalizovati MT5 u get_symbol_data()")
        return None

    tf = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_M5)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    mt5.shutdown()

    if rates is None:
        log.warning(f"⚠️ Nema dostupnih podataka za simbol {symbol}")
        return None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

class MT5ConnectionManager:
    def __init__(self):
        self.reconnect_mode = False
        self.stop_thread = threading.Event()

    def start(self):
        threading.Thread(target=self._watch_connection, daemon=True).start()

    def _watch_connection(self):
        while not self.stop_thread.is_set():
            if self.reconnect_mode:
                log.warning("⚠️ MT5 konekcija izgubljena, pokušavam reconnect...")
                settings = load_settings()
                success = connect_to_mt5(
                    path=settings.get("path"),
                    login=int(settings.get("login")),
                    password=settings.get("password"),
                    server=settings.get("server")
                )
                if success:
                    log.info("✅ MT5 konekcija uspostavljena ponovo.")
                    self.reconnect_mode = False
                else:
                    log.error("❌ Ponovni pokušaj konekcije nije uspeo.")
                time.sleep(15)
            else:
                time.sleep(1)

    def notify_connection_lost(self):
        if not self.reconnect_mode:
            log.warning("⚠️ Prelazak u reconnect mod zbog prekida veze sa MT5.")
            self.reconnect_mode = True

    def stop(self):
        self.stop_thread.set()
