from logs.logger import log

def is_abnormal_trade(profit, average_profit, threshold=3.0, min_absolute=100.0):
    """
    Detektuje da li je trejd abnormalan (prevelik dobitak/gubitak).

    :param profit: Profit tog trejda
    :param average_profit: Prosečan profit za taj simbol
    :param threshold: Koliko puta mora da bude veći ili manji da bi bio sumnjiv
    :param min_absolute: Minimalni apsolutni prag ako je average_profit blizu nule
    :return: True ako je abnormalan, False ako je normalan
    """
    # Ako nemamo dovoljno istorije ili prosečan profit previše mali
    if average_profit is None or abs(average_profit) < 0.01:
        result = abs(profit) >= min_absolute
        log.debug(f"[📊 AbnormalCheck] Bez istorije ili mali prosek. Profit={profit}, Prag={min_absolute} ➝ {result}")
        return result

    result = abs(profit) > abs(average_profit) * threshold
    log.debug(f"[📊 AbnormalCheck] Profit={profit}, Prosek={average_profit}, Prag={threshold}x ➝ {result}")
    return result
