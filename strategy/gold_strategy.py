import MetaTrader5 as mt5
from utils.indicator_data import get_live_indicators
from ai.gold_trade import predict_gold_trade  # ili kako već zoveš funkciju
from logs.logger import log

SYMBOL = "XAUUSD"
LOT = 0.1

def gold_strategy():
    features = get_live_indicators(symbol=SYMBOL)
    print("Feature dict pred AI:", features)
    log.info(f"Feature dict pred AI: {features}")

    if features is None:
        log.warning("Nema dostupnih indikatora za gold_strategy.")
        return

    required_features = [
        "rsi", "macd", "ema10", "ema30", "close", "volume",
        "spread", "adx", "stochastic", "cci", "gold_trend"
    ]
    missing = [feat for feat in required_features if feat not in features]
    if missing:
        log.error(f"Nedostaju feature-i za gold_strategy: {missing}")
        print("Nedostaju feature-i za gold_strategy:", missing)
        return

    prediction = predict_gold_trade(features)
    print("AI prediction:", prediction)
    log.info(f"AI prediction: {prediction}")

    if prediction is None:
        log.warning("AI predikcija nije dostupna za gold_strategy.")
        return

    if prediction == 1:
        if open_position("buy"):
            log.info("Gold_strategy otvorila BUY.")
    elif prediction == -1:
        if open_position("sell"):
            log.info("Gold_strategy otvorila SELL.")
    else:
        log.info("Gold_strategy – nema signala za trade.")

def open_position(direction):
    if not mt5.initialize():
        log.error("MetaTrader5 nije inicijalizovan!")
        return False

    try:
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            log.error("Nema tick podataka za simbol.")
            return False

        price = tick.ask if direction == "buy" else tick.bid
        order_type = mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": LOT,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "GoldStrategyAI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        else:
            log.error(f"Trade greška: {result.retcode}")
            return False

    except Exception as e:
        log.error(f"Greška u open_position: {e}")
        return False
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    gold_strategy()
