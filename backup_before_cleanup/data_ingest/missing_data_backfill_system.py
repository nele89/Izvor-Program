import os
import threading
import time
from datetime import datetime, timedelta
from collections import deque

import duckdb
import requests

# ---------------------------------------------
# Data model for a single bar (candle)
# ---------------------------------------------
class Bar:
    def __init__(self, ts, open_, high, low, close, volume):
        self.ts = ts             # datetime
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


# ---------------------------------------------
# Persistent storage using DuckDB
# ---------------------------------------------
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

    def save_temp_bar(self, bar: Bar):
        self.con.execute(
            """
            INSERT INTO bars (ts, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, 'temp')
            ON CONFLICT(ts) DO NOTHING;
            """,
            [bar.ts, bar.open, bar.high, bar.low, bar.close, bar.volume]
        )

    def save_official_bar(self, bar: Bar):
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


# ---------------------------------------------
# Ingestor: real-time + sliding-window backfill
# ---------------------------------------------
class DataIngestor:
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        store: DataStore,
        backfill_hours: int = 5,
        backfill_interval_sec: int = 60
    ):
        # avoid circular import by importing here
        from backend.chart_connector import ChartAPI

        self.symbol = symbol
        self.timeframe = timeframe
        self.store = store
        self.backfill_hours = backfill_hours
        self.backfill_interval = backfill_interval_sec

        # buffer for recent bars to drive any UI or in-memory logic
        bars_per_hour = 60 if timeframe.upper().endswith('M1') else 1
        self.buffer = deque(maxlen=bars_per_hour * backfill_hours)
        self.last_ts = self.store.get_latest_timestamp()

        # chart API: must implement .on_new_bar and .get_historical_bars
        self.chart_api = ChartAPI(symbol=self.symbol, timeframe=self.timeframe)
        self.chart_api.on_new_bar(self._on_new_bar)

    def _on_new_bar(self, bar: Bar):
        # store temp bar only if it's newer
        if bar.ts > self.last_ts:
            self.store.save_temp_bar(bar)
            self.buffer.append(bar)
            self.last_ts = bar.ts

    def _has_official(self, ts: datetime) -> bool:
        row = self.store.con.execute(
            "SELECT source FROM bars WHERE ts = ?",
            [ts]
        ).fetchone()
        return bool(row and row[0] == 'official')

    def _backfill_loop(self):
        while True:
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            for h in range(1, self.backfill_hours + 1):
                ts = now - timedelta(hours=h)
                # if missing or only temp exists, fetch official
                if not self._has_official(ts) or ts > self.last_ts:
                    try:
                        bars = self.chart_api.get_historical_bars(
                            start=ts,
                            end=ts + timedelta(hours=1)
                        )
                        for bar in bars:
                            self.store.save_official_bar(bar)
                            if bar.ts > self.last_ts:
                                self.buffer.append(bar)
                                self.last_ts = bar.ts
                    except Exception as e:
                        print(f"[Backfill error] {e}")
            time.sleep(self.backfill_interval)

    def start(self):
        # start real-time ingest
        self.chart_api.connect()
        # start backfill in background
        threading.Thread(target=self._backfill_loop, daemon=True).start()


# ---------------------------------------------
# Entrypoint
# ---------------------------------------------
def main():
    symbol = "EURUSD"
    timeframe = "M1"

    store = DataStore(db_path="local.duckdb")
    ingestor = DataIngestor(
        symbol=symbol,
        timeframe=timeframe,
        store=store,
        backfill_hours=5,
        backfill_interval_sec=60
    )
    ingestor.start()

    # keep process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")


if __name__ == "__main__":
    main()
