from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from utils.settings_handler import load_settings, save_settings

class AISettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ai_settings.ui", self)  # Ako je UI fajl u folderu /ui/

        # Učitaj postojeća podešavanja
        settings = load_settings()

        # Postavi vrednosti za svećice i last N trades
        self.candlesToAnalyzeSpinBox.setMinimum(100)
        self.candlesToAnalyzeSpinBox.setMaximum(100000)
        self.candlesToAnalyzeSpinBox.setValue(int(settings.get("ai_max_candles", 1000)))

        self.lastNTradesSpinBox.setMinimum(10)
        self.lastNTradesSpinBox.setMaximum(10000)
        self.lastNTradesSpinBox.setValue(int(settings.get("ai_training_last_n", 500)))

        # Dropdown za scope
        scope = settings.get("ai_training_scope", "All trades")
        index = self.learningScopeDropdown.findText(scope)
        if index != -1:
            self.learningScopeDropdown.setCurrentIndex(index)

        # Sakrij/pokaži last N polje prema izboru
        self.learningScopeDropdown.currentIndexChanged.connect(self.toggle_last_n_field)
        self.toggle_last_n_field(self.learningScopeDropdown.currentIndex())

        # Dugme za ručno treniranje
        self.btnTrainNow.clicked.connect(self.train_now)

        # Dugme za snimanje podešavanja
        self.btnSaveSettings.clicked.connect(self.save_settings)

    def toggle_last_n_field(self, index):
        text = self.learningScopeDropdown.currentText()
        is_last_n = "Last" in text
        self.lastNTradesSpinBox.setVisible(is_last_n)
        self.findChild(QtWidgets.QLabel, "lastNTradesLabel").setVisible(is_last_n)

    def train_now(self):
        try:
            from ai.ai_trainer import train_ai_model
            train_ai_model()
            QMessageBox.information(self, "AI Trening", "✅ AI trening uspešno pokrenut.")
        except Exception as e:
            QMessageBox.critical(self, "Greška", f"❌ AI trening nije pokrenut: {e}")

    def save_settings(self):
        settings = load_settings()

        # Preuzmi vrednosti iz forme
        settings["ai_max_candles"] = self.candlesToAnalyzeSpinBox.value()
        settings["ai_training_last_n"] = self.lastNTradesSpinBox.value()
        settings["ai_training_scope"] = self.learningScopeDropdown.currentText()

        save_settings(settings)
        QMessageBox.information(self, "Sačuvano", "✅ Podešavanja uspešno sačuvana.")
