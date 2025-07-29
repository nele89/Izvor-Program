import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from backend.mt5_connector import get_open_positions

class LivePositionWindow(QtWidgets.QDialog):
    def __init__(self, symbol="XAUUSD"):
        super().__init__()
        self.symbol = symbol
        # Učitaj UI fajl
        uic.loadUi(os.path.join("ui", "live_position.ui"), self)
        self.setWindowTitle(f"Otvorene pozicije - {symbol}")

        # Pronađi element tabele i dugmeta za osvežavanje
        self.table = self.findChild(QtWidgets.QTableWidget, "tablePositions")
        self.btnRefresh = self.findChild(QtWidgets.QPushButton, "btnRefresh")

        # Poveži dugme osvežavanja ako postoji
        if self.btnRefresh:
            self.btnRefresh.clicked.connect(self.load_positions)

        # Timer za automatsko osvežavanje svakih 5000 ms (5 sekundi)
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_positions)
        self.timer.start(5000)

        # Prvo učitavanje pozicija
        self.load_positions()

    def load_positions(self):
        try:
            positions = get_open_positions(self.symbol)
            self.table.clearContents()
            self.table.setRowCount(len(positions))
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "Ticket", "Symbol", "Type", "Lot", "Entry Price", "Profit ($)"
            ])

            for row, pos in enumerate(positions):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(pos.ticket)))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(pos.symbol))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem("BUY" if pos.type == 0 else "SELL"))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(pos.volume)))
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(round(pos.price_open, 4))))
                self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{pos.profit:.2f}"))

            self.table.resizeColumnsToContents()

        except Exception as e:
            print(f"[Greška pri učitavanju pozicija] {e}")
