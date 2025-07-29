import duckdb
from datetime import datetime


class DataStore:
    def __init__(self, db_path: str = 'local.duckdb'):
        self.con = duckdb.connect(db_path)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS bars (
                ts TIMESTAMP PRIMARY KEY,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE,
                source VARCHAR
            );
        """)

    def get_latest_timestamp(self) -> datetime:
        res = self.con.execute("SELECT MAX(ts) FROM bars").fetchone()[0]
        return res if res is not None else datetime(1970, 1, 1)

    def save_temp_bar(self, bar):  # bar must have attributes ts, open, high, low, close, volume
        self.con.execute(
            """
            INSERT INTO bars (ts, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, 'temp')
            ON CONFLICT(ts) DO NOTHING;
            """,
            [bar.ts, bar.open, bar.high, bar.low, bar.close, bar.volume]
        )

    def save_official_bar(self, bar):
        self.con.execute(
            """
            INSERT INTO bars (ts, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, 'official')
            ON CONFLICT(ts) DO UPDATE
              SET open    = EXCLUDED.open,
                  high    = EXCLUDED.high,
                  low     = EXCLUDED.low,
                  close   = EXCLUDED.close,
                  volume  = EXCLUDED.volume,
                  source  = 'official'
            WHERE bars.source = 'temp';
            """,
            [bar.ts, bar.open, bar.high, bar.low, bar.close, bar.volume]
        )

    def fetch_bars(self, from_ts: datetime, to_ts: datetime):
        return self.con.execute(
            """
            SELECT ts, open, high, low, close, volume
            FROM bars
            WHERE ts BETWEEN ? AND ?
            ORDER BY ts
            """,
            [from_ts, to_ts]
        ).fetchall()
