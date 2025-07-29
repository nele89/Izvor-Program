# engine/trade_manager.py

from utils.db_manager import insert_trade, update_decision_result
from datetime import datetime

def log_trade_and_update_ai(trade_data):
    """
    Upisuje trejd u bazu i ažurira AI odluku sa ishodom (win/loss).
    :param trade_data: dict sa ključevima:
        - symbol
        - entry_time (timestamp koji je AI odluka koristila)
        - exit_time
        - position_type ('buy' ili 'sell')
        - entry_price
        - exit_price
        - stop_loss
        - take_profit
        - profit
        - duration
        - opened_by ('ai' ili 'manual')
    """

    # Izračunavanje ishoda
    outcome = "win" if trade_data["profit"] > 0 else "loss"

    # Priprema tuple za insert
    insert_tuple = (
        trade_data["symbol"],
        trade_data["entry_time"],
        trade_data["exit_time"],
        trade_data["position_type"],
        float(trade_data["entry_price"]),
        float(trade_data["exit_price"]),
        float(trade_data["stop_loss"]),
        float(trade_data["take_profit"]),
        float(trade_data["profit"]),
        trade_data["duration"],
        trade_data["opened_by"],
        outcome
    )

    insert_trade(insert_tuple)

    # Ažuriranje AI odluke (ako postoji odluka sa tim vremenom i simbolom)
    try:
        update_decision_result(
            symbol=trade_data["symbol"],
            timestamp=trade_data["entry_time"],
            result=outcome
        )
    except Exception as e:
        print(f"[AI povezivanje greška] Nije moguće ažurirati odluku: {e}")
