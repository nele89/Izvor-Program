import MetaTrader5 as mt5
from logs.logger import log
from ai.signal_engine import get_trade_signal, calculate_tp_sl
from backend.mt5_connector import get_open_positions, open_trade
from utils.notifier import send_notification, send_popup_alert


def notify_all(msg):
    send_notification(msg)
    send_popup_alert(msg)


def execute_trade(signal, settings):
    symbol = settings.get("symbol", "XAUUSD")
    lot = float(settings.get("lot", 0.01))
    max_positions = int(settings.get("max_open_positions", 10))

    enable_scalping = settings.get("scalping_mode", "no").lower() == "yes"
    max_scalping_positions = int(settings.get("max_scalping_positions", 5))

    open_trades = get_open_positions(symbol)
    if open_trades is None:
        msg = f"⚠️ Ne mogu da dobijem broj otvorenih pozicija za {symbol}"
        log.warning(msg)
        notify_all(msg)
        return

    current_open = len(open_trades)
    max_allowed = max_scalping_positions if enable_scalping else max_positions

    if current_open >= max_allowed:
        msg = f"❌ Dosegnut maksimalan broj pozicija ({max_allowed}) za {symbol}."
        log.warning(msg)
        notify_all(msg)
        return

    strategy = settings.get("tp_sl_strategy", "dynamic")
    percentage = float(settings.get("tp_percentage", 1.5))
    atr_period = int(settings.get("atr_period", 14))
    atr_multiplier = float(settings.get("atr_multiplier", 2.0))

    tp, sl = calculate_tp_sl(
        symbol=symbol,
        signal=signal,
        strategy=strategy,
        percentage=percentage,
        atr_period=atr_period,
        atr_multiplier=atr_multiplier
    )

    if enable_scalping:
        tp *= 0.4
        sl *= 0.4
        log.info(f"⚡ Skalping mod aktivan – TP i SL umanjeni: TP={tp:.2f}, SL={sl:.2f}")

    if signal == "buy":
        result = open_trade(symbol, lot, mt5.ORDER_TYPE_BUY, tp=tp, sl=sl)
    elif signal == "sell":
        result = open_trade(symbol, lot, mt5.ORDER_TYPE_SELL, tp=tp, sl=sl)
    else:
        log.info("ℹ️ Nema validnog signala za trgovinu.")
        return

    if result:
        msg = f"✅ Otvorena {signal.upper()} pozicija za {symbol} (TP: {tp:.2f}, SL: {sl:.2f})"
        log.info(msg)
        notify_all(msg)
    else:
        msg = f"❌ Neuspešno otvaranje {signal.upper()} pozicije za {symbol}"
        log.warning(msg)
        notify_all(msg)


def run_trading_logic(settings):
    symbol = settings.get("symbol", "XAUUSD")
    timeframe = settings.get("timeframe", "M5")

    signal = get_trade_signal(symbol, timeframe=timeframe, settings=settings)

    if signal:
        msg = f"📈 Signal detektovan za {symbol}: {signal.upper()}"
        log.info(msg)
        notify_all(msg)
        execute_trade(signal, settings)
    else:
        log.info(f"ℹ️ Nema trejd signala trenutno za {symbol}.")
