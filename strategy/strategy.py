import pandas as pd
from logs.logger import log
from ai.predictors.combine_predictions import combine_predictions
from utils.news_state import get_latest_news_text

# Primer funkcije koja pokreće strategiju

def run_strategy(df):
    """
    Pokreće AI strategiju i vraća finalni signal
    df: DataFrame sa tržišnim podacima (ohlcv + indikatori)
    """
    try:
        # Uzimanje teksta poslednje vesti
        news_text = get_latest_news_text()
        
        # Kombinovanje svih AI predikcija
        signal = combine_predictions(df, news_text)

        if signal is None:
            log.warning("⚠️ AI nije dao signal - fallback na HOLD")
            return 1  # default HOLD

        log.info(f"✅ Finalni AI signal: {signal} (0=SELL, 1=HOLD, 2=BUY)")
        return signal

    except Exception as e:
        log.error(f"❌ Greška u run_strategy: {e}")
        return 1  # fallback na HOLD
