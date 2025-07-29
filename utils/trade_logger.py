import os
import pandas as pd
from datetime import datetime
from logs.logger import log
from utils.model_predictor import predict_trade  # <-- ispravan import

# Putanja gde se čuvaju trades i features kao Parquet fajlovi
TRADES_PARQUET = os.path.join("data", "trades.parquet")
FEATURES_PARQUET = os.path.join("data", "trade_features.parquet")

def log_trade(symbol, position_type, volume, entry_price, result="pending"):
    try:
        entry_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        trade = {
            "symbol": symbol,
            "position_type": position_type,
            "volume": volume,
            "entry_price": entry_price,
            "entry_time": entry_time,
            "result": result
        }

        # Ako fajl ne postoji, kreiraj DataFrame i snimi
        if not os.path.exists(TRADES_PARQUET):
            df = pd.DataFrame([trade])
        else:
            df = pd.read_parquet(TRADES_PARQUET)
            df = pd.concat([df, pd.DataFrame([trade])], ignore_index=True)
        df.to_parquet(TRADES_PARQUET, index=False)
        trade_id = len(df)  # koristi redni broj kao ID (nije baš kao auto_increment ali radi posao)
        log.info(f"📝 Trade zabeležen: {symbol} {position_type} {volume} @ {entry_price}")
        return trade_id

    except Exception as e:
        log.error(f"❌ Greška pri upisu trejda: {e}")
        return None

def log_trade_features(trade_id, rsi, macd, ema_diff, volume, spread, volatility,
                       dxy_value, us30_trend, spx500_trend, label=None):
    try:
        feature = {
            "trade_id": trade_id,
            "rsi": rsi,
            "macd": macd,
            "ema_diff": ema_diff,
            "volume": volume,
            "spread": spread,
            "volatility": volatility,
            "dxy_value": dxy_value,
            "us30_trend": us30_trend,
            "spx500_trend": spx500_trend,
            "label": label
        }
        if not os.path.exists(FEATURES_PARQUET):
            df = pd.DataFrame([feature])
        else:
            df = pd.read_parquet(FEATURES_PARQUET)
            df = pd.concat([df, pd.DataFrame([feature])], ignore_index=True)
        df.to_parquet(FEATURES_PARQUET, index=False)
        log.info(f"📊 Trade feature dodati za trade_id: {trade_id}")

    except Exception as e:
        log.error(f"❌ Greška pri upisu feature-a: {e}")

def log_trade_and_update_ai(symbol, position_type, entry_price, indicator_data):
    try:
        volume = indicator_data.get("volume", 0.01)

        # 📝 Loguj trejd
        trade_id = log_trade(symbol, position_type, volume, entry_price, result="pending")

        # 🤖 AI predikcija
        try:
            prediction = predict_trade(**indicator_data)
        except Exception as e:
            prediction = "error"
            log.warning(f"⚠️ AI predikcija nije uspela: {e}")

        # 📊 Loguj feature-e
        log_trade_features(
            trade_id=trade_id,
            rsi=indicator_data.get("rsi"),
            macd=indicator_data.get("macd"),
            ema_diff=indicator_data.get("ema_diff"),
            volume=volume,
            spread=indicator_data.get("spread"),
            volatility=indicator_data.get("volatility"),
            dxy_value=indicator_data.get("dxy_value"),
            us30_trend=indicator_data.get("us30_trend"),
            spx500_trend=indicator_data.get("spx500_trend"),
            label=1 if position_type == "buy" else 0
        )

        log.info(f"✅ Trejd sa ID {trade_id} i AI='{prediction}' zabeležen.")
        return trade_id

    except Exception as e:
        log.error(f"❌ Neuspelo logovanje trejda i AI predikcije: {e}")
        return None
