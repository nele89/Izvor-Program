import os
from datetime import datetime
from data.downloader.dukascopy_downloader import download_data

# ✅ Lista najvažnijih valutnih parova i instrumenata
symbols = [
    "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
    "AUDUSD", "NZDUSD", "USDCAD", "BTCUSD", "ETHUSD"
]

# ✅ Timeframe-ovi u sekundama (za dukascopy-python)
timeframes = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600
}

# ✅ Opseg datuma koji želiš da skidaš
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

# ✅ Glavna putanja za snimanje podataka
BASE_DIR = os.path.join("data", "dukascopy")
os.makedirs(BASE_DIR, exist_ok=True)

def download_all_data():
    for symbol in symbols:
        symbol_dir = os.path.join(BASE_DIR, symbol)
        os.makedirs(symbol_dir, exist_ok=True)

        for tf_name, tf_sec in timeframes.items():
            print(f"⏳ Skidanje {symbol} - {tf_name} ...")
            try:
                df = download_data(symbol, tf_sec, start_date, end_date)
                if df is not None and not df.empty:
                    filename = os.path.join(symbol_dir, f"{symbol}_{tf_name}.csv")
                    df.to_csv(filename, index=False)
                    print(f"✅ Sačuvano: {filename}")
                else:
                    print(f"⚠️ Nema podataka za {symbol} - {tf_name}")
            except Exception as e:
                print(f"❌ Greška pri preuzimanju {symbol} - {tf_name}: {e}")

if __name__ == "__main__":
    download_all_data()
