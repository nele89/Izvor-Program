# utils/monitor_closed.py

import MetaTrader5 as mt5
from logs.logger import log
from utils.trade_logger import log_trade_and_update_ai
from utils.indicator_data import get_live_indicators

def fetch_and_log_closed_trades(symbol="XAUUSD"):
    try:
        # 🔍 Dohvati zatvorene pozicije
        history = mt5.history_deals_get(position=0)
        if history is None or len(history) == 0:
            log.info("ℹ️ Nema zatvorenih trejdova u istoriji.")
            return

        # 🧠 Preuzmi indikatore za trenutni simbol
        indicator_data = get_live_indicators(symbol)
        if not indicator_data:
            log.warning("⚠️ Nema dostupnih indikatora za logovanje zatvorenog trejda.")
            return

        # 📝 Prođi kroz zatvorene trejdove i loguj
        for deal in history:
            if deal.symbol != symbol:
                continue

            if deal.type == mt5.ORDER_TYPE_BUY:
                position_type = "buy"
            elif deal.type == mt5.ORDER_TYPE_SELL:
                position_type = "sell"
            else:
                continue  # samo logujemo buy/sell

            entry_price = deal.price
            log_trade_and_update_ai(symbol, position_type, entry_price, indicator_data)

        log.info(f"✅ Obrađeno zatvorenih trejdova: {len(history)}")

    except Exception as e:
        log.error(f"❌ Greška prilikom logovanja zatvorenih trejdova: {e}")
