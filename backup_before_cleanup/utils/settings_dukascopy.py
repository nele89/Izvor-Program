# utils/settings_dukascopy.py

from datetime import datetime, timedelta

DUKASCOPY_SETTINGS = {
    "symbols": [
        "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "NZDUSD", "USDCAD"
    ],
    "start_date": datetime(2010, 1, 1),
    "end_date": datetime.utcnow(),
    "save_folder": "data/trading_data",
    "pause_seconds": 0.5
}

def generate_dukascopy_settings():
    return {
        "dukascopy": {
            "symbols": ["EURUSD"],  # samo EURUSD za test
            "target_folder": "data/dukascopy",
            "pause_seconds": 0.1,
            "start_date": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "end_date": datetime.utcnow().strftime("%Y-%m-%d")
        }
    }
