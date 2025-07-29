# threads/database_thread.py

from PyQt5.QtCore import QThread, pyqtSignal
from logs.logger import log  # Ako koristiš logovanje u fajl

class DatabaseThread(QThread):
    finished = pyqtSignal(object)  # Signal koji šalje rezultat nazad u GUI
    error = pyqtSignal(str)        # Signal za obaveštavanje o grešci

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            log.info(f"📥 [DatabaseThread] Pokrećem funkciju: {self.function.__name__}")
            result = self.function(*self.args, **self.kwargs)
            self.finished.emit(result)
            log.info(f"✅ [DatabaseThread] Završena funkcija: {self.function.__name__}")
        except Exception as e:
            self.finished.emit(None)
            self.error.emit(str(e))
            log.error(f"❌ [DatabaseThread greška] {e}")
