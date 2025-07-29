import os
from PyQt5 import QtWidgets, uic
from ui.live_position_window import LivePositionWindow
from ui.statistics_window import StatisticsWindow
from ui.closed_positions_window import ClosedPositionsWindow
from ui.ai_statistics_window import AIStatisticsWindow
from ui.settings_window import SettingsWindow

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        uic.loadUi(os.path.join("ui", "dashboard.ui"), self)

        self.btnStartStop = self.findChild(QtWidgets.QPushButton, "btnStartStop")
        self.btnStartStop.clicked.connect(self.toggle_trading)

        self.btnLivePositions = self.findChild(QtWidgets.QPushButton, "btnLivePositions")
        self.btnLivePositions.clicked.connect(self.open_live_positions)

        self.btnStatistics = self.findChild(QtWidgets.QPushButton, "btnStatistics")
        self.btnStatistics.clicked.connect(self.open_statistics)

        self.btnAIStats = self.findChild(QtWidgets.QPushButton, "btnAIStats")
        self.btnAIStats.clicked.connect(self.open_ai_statistics)

        self.btnClosed = self.findChild(QtWidgets.QPushButton, "btnClosed")
        self.btnClosed.clicked.connect(self.open_closed_positions)

        self.btnSettings = self.findChild(QtWidgets.QPushButton, "btnSettings")
        self.btnSettings.clicked.connect(self.open_settings)

        self.tabWidget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.currentChanged.connect(self.tab_changed)

        self.update_status()

    def toggle_trading(self):
        if self.btnStartStop.text().startswith("▶"):
            self.btnStartStop.setText("⏸ Zaustavi")
            print("✅ Trgovanje pokrenuto")
        else:
            self.btnStartStop.setText("▶ Pokreni")
            print("⏸ Trgovanje zaustavljeno")

    def update_status(self):
        # Dodaj ovde kasnije: update lampica, AI status i slično
        pass

    def open_live_positions(self):
        self.live_window = LivePositionWindow(symbol=self.settings.get("symbol", "XAUUSD"))
        self.live_window.exec_()

    def open_statistics(self):
        self.stats_window = StatisticsWindow(self.settings)
        self.stats_window.exec_()

    def open_ai_statistics(self):
        self.ai_stats_window = AIStatisticsWindow()
        self.ai_stats_window.exec_()

    def open_closed_positions(self):
        self.closed_window = ClosedPositionsWindow()
        self.closed_window.exec_()

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.exec_()

    def tab_changed(self, index):
        print(f"[INFO] Tab promenjen na indeks {index}")
        # Dodaj po potrebi: osvežavanje sadrzaja kada korisnik pređe na određeni tab
