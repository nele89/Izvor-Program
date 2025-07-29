import sqlite3
import os

# Putanja do baze
DB_PATH = os.path.join("db", "trading_ai_core.db")

# Poveži se na bazu
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Kreiraj tabelu ako ne postoji
cursor.execute("""
CREATE TABLE IF NOT EXISTS trade_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER,  -- opcionalno, ako budeš povezivao sa trades tabelom
    rsi REAL,
    macd REAL,
    ema_diff REAL,
    volume INTEGER,
    spread REAL,
    volatility REAL,
    dxy_value REAL,
    us30_trend INTEGER,
    spx500_trend INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ Tabela 'trade_features' je uspešno kreirana.")
