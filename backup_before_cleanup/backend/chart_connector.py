import threading
from datetime import datetime, timedelta
from typing import Callable, List

import requests

from data_ingest.missing_data_backfill_system import Bar


class ChartAPI:
    """
    Stub za konekciju na real-time chart ili MT5 stream.
    Omogućava prijavu callback-a za nove barove i dohvat istorijskih barova.
    """
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self._bar_listeners: List[Callable[[Bar], None]] = []
        self._running = False

    def on_new_bar(self, callback: Callable[[Bar], None]):
        """
        Registruje funkciju koja će biti pozvana kada stigne novi bar.
        """
        self._bar_listeners.append(callback)

    def connect(self):
        """
        Povezuje se na real-time izvor (npr. websocket ili MT5 stream).
        Pokreće pozadinski thread koji emituje Bar instance.
        """
        self._running = True
        threading.Thread(target=self._read_stream, daemon=True).start()

    def _read_stream(self):
        # TODO: Implementirati konekciju i parsiranje real-time podataka
        # Primer: Websocket na chart server ili MT5 Web API
        while self._running:
            # Čekaj novi bar ili tick, agregiraj u bar
            # bar = Bar(ts, open, high, low, close, volume)
            # for cb in self._bar_listeners:
            #     cb(bar)
            pass

    def get_historical_bars(self, start: datetime, end: datetime) -> List[Bar]:
        """
        Preuzima satne Barove sa Dukascopy HTTP feed-a između start i end.
        """
        bars: List[Bar] = []
        symbol = self.symbol
        ts = start.replace(minute=0, second=0, microsecond=0)
        while ts < end:
            url = (
                f"https://datafeed.dukascopy.com/datafeed/{symbol}/"
                f"{ts.year}/{ts.month:02d}/{ts.day:02d}/{ts.hour:02d}h_ticks.bi5"
            )
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    # TODO: Parse BI5 u listu tickova, agregiraj u Bar
                    # Primer: ticks = parse_bi5(resp.content)
                    # bar = aggregate_to_bar(ticks)
                    # bars.append(bar)
                    pass
            except Exception:
                pass
            ts += timedelta(hours=1)
        return bars

    def disconnect(self):
        """
        Zaustavlja real-time stream.
        """
        self._running = False
