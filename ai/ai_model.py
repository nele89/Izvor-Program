from ai.predictors.combine_predictions import combine_predictions
from logs.logger import log
from utils.news_state import get_latest_news_text


def predict_trade(df):
    """
    Vraća AI signal kombinovan iz 4 specijalizovana modela.
    Ulaz: df sa svim potrebnim kolona i najnovijim podacima.
    """
    try:
        news_text = get_latest_news_text()
        signal = combine_predictions(df, news_text)

        if signal is None:
            log.warning("⚠️ AI nije dao signal – koristi se default HOLD")
            return 1  # HOLD kao podrazumevana vrednost

        log.info(f"🧠 AI trade signal: {signal} (0=SELL, 1=HOLD, 2=BUY)")
        return signal

    except Exception as e:
        log.error(f"❌ Greška u predict_trade(): {e}")
        return 1
