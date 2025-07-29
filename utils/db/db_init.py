# db_init.py
import sqlite3
import os

DB_PATH = os.path.join("db", "trading_ai_core.db")

def create_tables():
    try:
        # Kreiraj folder db ako ne postoji
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Tabela trades
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
        )
        """)

        # Tabela trade_features
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER,
            rsi REAL,
            macd REAL,
            ema_diff REAL,
            volume REAL,
            spread REAL,
            volatility REAL,
            dxy_value REAL,
            us30_trend INTEGER,
            spx500_trend INTEGER,
            timestamp TEXT
        )
        """)

        # Tabela decision_memory
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            decision TEXT,
            explanation TEXT,
            result TEXT
        )
        """)

        # Tabela candle_patterns
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candle_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_time TEXT,
            symbol TEXT,
            pattern TEXT,
            outcome TEXT,
            success INTEGER
        )
        """)

        # Tabela news_sentiment
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            title TEXT,
            content TEXT,
            sentiment TEXT,
            related_symbol TEXT,
            effect_on_price TEXT
        )
        """)

        # Tabela ai_predictions (ako koristiš za čuvanje AI predviđanja)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            decision TEXT,
            explanation TEXT,
            result TEXT,
            created_at TEXT
        )
        """)

        conn.commit()
        conn.close()
        print("✅ Sve tabele su proverene/napravljene.")
    except Exception as e:
        print(f"❌ Greška pri inicijalizaciji baze: {e}")

if __name__ == "__main__":
    create_tables()
