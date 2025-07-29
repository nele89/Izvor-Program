import os
import joblib
import pandas as pd
from logs.logger import log

from ai.predictors.predict_trend import predict_trend
from ai.predictors.predict_volatility import predict_volatility
from ai.predictors.predict_sentiment import predict_sentiment
from ai.predictors.predict_orderflow import predict_orderflow

MODEL_PATH = os.path.join("ai", "models", "meta_model.pkl")

LABEL_MAP = {
    0: "SELL",
    1: "HOLD",
    2: "BUY"
}

def combine_predictions(df: pd.DataFrame, news_text: str) -> int | None:
    try:
        trend_signal = predict_trend(df)
        volatility_signal = predict_volatility(df)
        orderflow_signal = predict_orderflow(df)
        sentiment_label = predict_sentiment(news_text)

        sentiment_signal_map = {
            "negativan": 0,
            "neutralan": 1,
            "pozitivan": 2
        }
        sentiment_signal = sentiment_signal_map.get(sentiment_label, None)

        if None in (trend_signal, volatility_signal, orderflow_signal, sentiment_signal):
            log.warning("⚠️ Neka od 4 AI predikcije nije dostupna – nema odluke.")
            return None

        # Formiraj ulaz za meta-model
        X_meta = pd.DataFrame([{
            'trend_signal': int(round(trend_signal)),
            'volatility_signal': int(round(volatility_signal)) if isinstance(volatility_signal, (int, float)) else volatility_signal,
            'sentiment_signal': sentiment_signal,
            'orderflow_signal': orderflow_signal
        }])

        # Učitaj meta-model
        meta_model = joblib.load(MODEL_PATH)
        final_prediction = meta_model.predict(X_meta)[0]
        final_signal = LABEL_MAP.get(final_prediction, "NEPOZNATO")

        log.info(f"🧠 META-ODLUKA: {final_signal} (class={final_prediction})")
        return final_prediction  # 0, 1, 2

    except Exception as e:
        log.error(f"❌ Greška u combine_predictions: {e}")
        return None
