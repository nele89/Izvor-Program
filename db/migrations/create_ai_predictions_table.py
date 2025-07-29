import sqlite3
import os

# Putanja do SQLite baze
DB_PATH = os.path.join("db", "trading_ai_core.db")

# Konekcija sa bazom
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# SQL za kreiranje tabele ako ne postoji
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    decision TEXT,
    explanation TEXT,
    result TEXT DEFAULT 'pending',
    created_at TEXT
)
""")

conn.commit()
conn.close()

print("✅ ai_predictions tabela je kreirana ili već postoji.")
