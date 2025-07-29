import MetaTrader5 as mt5
from logs.logger import log
from utils.settings_handler import load_settings

SYMBOL = "XAUUSD"

def initialize_mt5():
    if not mt5.initialize():
        log.error(f"❌ MT5 nije uspešno inicijalizovan: {mt5.last_error()}")
        return False
    log.info("✅ MT5 inicijalizovan.")
    return True

def shutdown_mt5():
    mt5.shutdown()
    log.info("MT5 zatvoren.")

def get_symbol_info(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        log.error(f"❌ Simbol {symbol} nije pronađen u MT5.")
        return None
    if not info.visible:
        if not mt5.symbol_select(symbol, True):
            log.error(f"❌ Nije uspelo selektovanje simbola {symbol}.")
            return None
    return info

def execute_trade(action, volume=0.01, price=None, deviation=10, comment="AutoTrade"):
    """
    action: 'buy' ili 'sell'
    volume: lot veličina
    price: cena za limit/stop, None za tržišnu
    deviation: maksimalna odstupanja u tačkama
    """
    if action not in ["buy", "sell"]:
        log.error(f"❌ Nepoznata akcija trejda: {action}")
        return False

    symbol_info = get_symbol_info(SYMBOL)
    if symbol_info is None:
        return False

    point = symbol_info.point
    price_bid = mt5.symbol_info_tick(SYMBOL).bid
    price_ask = mt5.symbol_info_tick(SYMBOL).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price_ask if action == "buy" else price_bid,
        "deviation": deviation,
        "magic": 123456,
        "comment": comment,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        log.error(f"❌ Trejd nije uspeo: {result.comment}")
        return False
    else:
        log.info(f"✅ Trejd uspešno poslat: {action} {volume} lot na {SYMBOL} po ceni {request['price']}")
        return True

if __name__ == "__main__":
    if initialize_mt5():
        execute_trade("buy", volume=0.01)
        shutdown_mt5()
