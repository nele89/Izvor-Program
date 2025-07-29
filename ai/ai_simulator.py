import time
from logs.logger import log
from utils.data_loader import load_symbol_data
from ai.ai_model import predict_trade
from utils.db_manager import insert_simulated_trade

def get_indicators_from_row(row):
    # Pretpostavka: tvoj CSV/DF već ima ove kolone
    return {
        "rsi": row.get("rsi", 50),
        "macd": row.get("macd", 0),
        "ema_diff": row.get("ema_diff", 0),
        "volume": row.get("volume", 100000),
        "spread": row.get("spread", 0.1),
        "volatility": row.get("volatility", 1.0),
        "dxy_value": row.get("dxy_value", 100.0),
        "us30_trend": row.get("us30_trend", 0),
        "spx500_trend": row.get("spx500_trend", 0),
    }

def run_simulation(symbol, timeframe="M1", max_steps=None, pause=0.01):
    log.info(f"🚦 Pokrećem AI simulaciju za {symbol} ({timeframe}) ...")
    df = load_symbol_data(symbol, timeframe)
    if df is None or df.empty:
        log.warning("❌ Nema podataka za simulaciju.")
        return

    steps = len(df) if max_steps is None else min(len(df), max_steps)
    results = []
    for idx, row in df.head(steps).iterrows():
        indicators = get_indicators_from_row(row)
        decision = predict_trade(**indicators)
        if decision:
            insert_simulated_trade(symbol, decision, indicators)
            results.append((row["time"], decision))
            log.info(f"🟠 Simulacija {symbol}: {row['time']} -> {decision}")
        else:
            log.info(f"⏩ Preskočeno {symbol} {row['time']} (nema AI odluke)")
        time.sleep(pause)

    log.info(f"🏁 Simulacija gotova: {symbol} ({len(results)} trejdova od {steps} koraka)")
    return results

def run_multi_simulation(symbols, timeframe="M1", **kwargs):
    all_results = {}
    for symbol in symbols:
        result = run_simulation(symbol, timeframe, **kwargs)
        all_results[symbol] = result
    return all_results

if __name__ == "__main__":
    # Primer: pokreni AI simulaciju za sve najvažnije simbole
    SIMBOLI = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
    run_multi_simulation(SIMBOLI, timeframe="M1", max_steps=1000, pause=0.005)
