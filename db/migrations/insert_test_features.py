import sqlite3
import os
import random

DB_PATH = os.path.join("db", "trading_ai_core.db")

def insert_test_features():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for i in range(15):  # Unesi 15 redova
        cursor.execute("""
            INSERT INTO trade_features (
                trade_id,
                rsi,
                macd,
                ema_diff,
                volume,
                spread,
                volatility,
                dxy_value,
                us30_trend,
                spx500_trend,
                label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,                                      # povezuje sa testnim trejdom
            random.uniform(20, 80),                 # RSI
            random.uniform(-0.01, 0.01),            # MACD
            random.uniform(-2.0, 2.0),              # EMA diff
            random.randint(50000, 200000),          # Volume
            random.uniform(0.1, 0.5),               # Spread
            random.uniform(0.5, 3.0),               # Volatility
            random.uniform(99.0, 106.0),            # DXY
            random.choice([-1, 0, 1]),              # US30 trend
            random.choice([-1, 0, 1]),              # SPX500 trend
            random.choice([0, 1])                   # Label (0 = sell, 1 = buy)
        ))

    conn.commit()
    conn.close()
    print("✅ Ubaceno 15 test redova u 'trade_features'.")

if __name__ == "__main__":
    insert_test_features()
