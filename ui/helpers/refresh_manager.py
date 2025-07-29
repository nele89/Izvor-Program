# ui/helpers/refresh_manager.py

from PyQt5.QtCore import QTimer

class RefreshManager:
    def __init__(self, interval_ms=1000):
        self.interval_ms = interval_ms  # npr. 1000 = 1 sekunda
        self.callbacks = []
        self.timer = QTimer()
        self.timer.timeout.connect(self._run_callbacks)
        self.active = False

    def _run_callbacks(self):
        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                print(f"❌ Greška u refresh callback-u: {e}")

    def register_callback(self, func):
        """Dodaje funkciju koja će se pozivati pri svakom intervalu."""
        if callable(func) and func not in self.callbacks:
            self.callbacks.append(func)

    def unregister_callback(self, func):
        """Uklanja prethodno registrovanu funkciju."""
        if func in self.callbacks:
            self.callbacks.remove(func)

    def start(self):
        """Pokreće automatski refresh."""
        if not self.active:
            self.timer.start(self.interval_ms)
            self.active = True

    def stop(self):
        """Zaustavlja refresh ciklus."""
        if self.active:
            self.timer.stop()
            self.active = False

    def set_interval(self, new_interval_ms):
        """Promeni interval osvežavanja u toku rada."""
        self.interval_ms = new_interval_ms
        if self.active:
            self.stop()
            self.start()
