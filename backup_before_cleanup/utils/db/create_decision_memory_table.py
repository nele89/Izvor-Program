import sqlite3
import os

DB_PATH = os.path.join("db", "trading_ai_core.db")

def create_decision_memory_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            symbol TEXT,
            decision TEXT,
            explanation TEXT,
            result TEXT
        );
    """)

    conn.commit()
    conn.close()
    print("✅ decision_memory tabela uspešno kreirana.")

if __name__ == "__main__":
    create_decision_memory_table()
