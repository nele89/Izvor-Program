import sqlite3
import os

DB_PATH = os.path.join("db", "trading_ai_core.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Dodaj dxy_value kolonu
try:
    cursor.execute("ALTER TABLE trade_features ADD COLUMN dxy_value REAL;")
    print("✅ dxy_value kolona dodata.")
except Exception as e:
    print(f"⚠️ dxy_value kolona već postoji ili greška: {e}")

# Dodaj us30_trend kolonu
try:
    cursor.execute("ALTER TABLE trade_features ADD COLUMN us30_trend INTEGER;")
    print("✅ us30_trend kolona dodata.")
except Exception as e:
    print(f"⚠️ us30_trend kolona već postoji ili greška: {e}")

# Dodaj spx500_trend kolonu
try:
    cursor.execute("ALTER TABLE trade_features ADD COLUMN spx500_trend INTEGER;")
    print("✅ spx500_trend kolona dodata.")
except Exception as e:
    print(f"⚠️ spx500_trend kolona već postoji ili greška: {e}")

conn.commit()
conn.close()
