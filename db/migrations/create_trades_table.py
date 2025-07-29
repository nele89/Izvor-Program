import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "trading_ai_core.db")
DB_PATH = os.path.abspath(DB_PATH)

def create_trades_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            entry_time TEXT,
            exit_time TEXT,
            position_type TEXT,
            entry_price REAL,
            exit_price REAL,
            stop_loss REAL,
            take_profit REAL,
            profit REAL,
            duration REAL,
            opened_by TEXT,
            outcome TEXT
        );
    """)
    conn.commit()
    conn.close()
    print(f"✅ Tabela 'trades' uspešno kreirana u {DB_PATH}")

if __name__ == "__main__":
    create_trades_table()
