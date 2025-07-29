from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt


class AIPredictionDisplay(QWidget):
    def __init__(self, parent=None):
        super(AIPredictionDisplay, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.title = QLabel("🧠 AI Predikcije (real-time)")
        self.title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Simbol", "Predikcija", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def update_predictions(self, prediction_data):
        """
        prediction_data format:
        [
            {"symbol": "XAUUSD", "prediction": "BUY", "status": "active"},
            {"symbol": "EURUSD", "prediction": "SELL", "status": "paused"},
            ...
        ]
        """
        self.table.setRowCount(len(prediction_data))
        for row, data in enumerate(prediction_data):
            self.table.setItem(row, 0, QTableWidgetItem(data.get("symbol", "")))
            self.table.setItem(row, 1, QTableWidgetItem(data.get("prediction", "")))

            status_item = QTableWidgetItem(data.get("status", ""))
            if data.get("status") == "active":
                status_item.setBackground(Qt.green)
            elif data.get("status") == "paused":
                status_item.setBackground(Qt.yellow)
            elif data.get("status") == "error":
                status_item.setBackground(Qt.red)
            else:
                status_item.setBackground(Qt.gray)

            self.table.setItem(row, 2, status_item)
