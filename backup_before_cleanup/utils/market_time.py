from datetime import datetime

def is_market_open():
    now = datetime.utcnow()
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday
    hour = now.hour

    # Forex: Otvoreno od nedelje 22h do petka 22h (UTC)
    if weekday == 6 and hour >= 22:
        return True
    elif weekday in [0, 1, 2, 3]:
        return True
    elif weekday == 4 and hour < 22:
        return True
    return False
