import time
from threading import Thread

# Provera da li je logger pravilno importovan
try:
    from logs.logger import log
except ImportError:
    import logging
    log = logging.getLogger("live_stats_updater")
    logging.basicConfig(level=logging.INFO)

from backend.mt5_connector import get_account_info, get_open_positions


class LiveStatsUpdater(Thread):
    def __init__(self, update_callback, interval=5):
        super().__init__()
        self.update_callback = update_callback  # Callback za slanje podataka GUI-ju
        self.interval = interval
        self.running = True
        self.daemon = True  # Da se thread automatski zatvori sa programom

    def run(self):
        log.info("📡 Live stats updater pokrenut.")
        while self.running:
            try:
                stats = self.get_stats()
                self.update_callback(stats)
            except Exception as e:
                log.warning(f"⚠️ Live stats greška: {e}")
            time.sleep(self.interval)
        log.info("🛑 Live stats updater zaustavljen.")

    def stop(self):
        self.running = False

    def get_stats(self):
        info = get_account_info()
        positions = get_open_positions()

        profit_total = sum(p.profit for p in positions) if positions else 0
        win_trades = [p for p in positions if p.profit > 0]
        win_rate = (len(win_trades) / len(positions)) * 100 if positions else 0

        stats = {
            "balance": info.get("balance", 0),
            "profit": profit_total,
            "trades": len(positions),
            "win_rate": f"{win_rate:.1f}%",
            "drawdown": f"{(info.get('balance', 0) - info.get('equity', 0)):.2f}",
            "avg_time": "-",  # Ovde se može ubaciti logika ako meriš vreme trajanja pozicija
        }
        return stats
