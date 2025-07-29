from PyQt5.QtWidgets import QMainWindow
from old.main_window_layout_final import Ui_MainWindow
from ui.components.checkable_combobox import CheckableComboBox
from utils.settings_handler import load_settings, save_settings

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_pair_selector()

        # Dugmad
        self.ui.startStopButton.clicked.connect(self.toggle_trading)
        self.ui.btnHome.clicked.connect(self.go_home)
        self.ui.btnAISettings.clicked.connect(self.open_ai_settings)
        self.ui.btnReports.clicked.connect(self.open_reports)
        self.ui.btnLivePositions.clicked.connect(self.open_live_positions)
        self.ui.btnApiNews.clicked.connect(self.open_api_news)
        self.ui.menuAdvancedWindowButton.clicked.connect(self.open_advanced_settings)
        self.ui.menuGeneralSettingsButton.clicked.connect(self.open_general_settings)

    def setup_pair_selector(self):
        # Zameni običan QComboBox sa CheckableComboBox
        parent_layout = self.ui.dropdownPairSelector.parent()
        layout = parent_layout.layout()
        index = layout.indexOf(self.ui.dropdownPairSelector)

        layout.removeWidget(self.ui.dropdownPairSelector)
        self.ui.dropdownPairSelector.deleteLater()

        self.combo = CheckableComboBox()
        self.combo.add_check_items([
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "USDCAD", "AUDUSD", "NZDUSD", "XAUUSD"
        ])
        layout.insertWidget(index, self.combo)

        self.load_selected_pairs()
        self.combo.view().pressed.connect(lambda _: self.save_selected_pairs())

    def save_selected_pairs(self):
        selected = self.combo.checked_items()
        settings = load_settings()
        settings["selected_pairs"] = selected
        save_settings(settings)
        print(f"💾 Sačuvani valutni parovi: {selected}")
        self.apply_symbol_selection_to_backend(selected)

    def load_selected_pairs(self):
        settings = load_settings()
        selected = settings.get("selected_pairs", [])
        for i in range(self.combo.model().rowCount()):
            item = self.combo.model().item(i)
            if item.text() in selected:
                item.setCheckState(2)  # Qt.Checked
        self.combo.update_display_text()
        self.apply_symbol_selection_to_backend(selected)

    def apply_symbol_selection_to_backend(self, selected_pairs):
        print(f"📡 Aktivni simboli za analizu: {selected_pairs}")
        # Ovde možeš povezati sa AI logikom, npr: ai_engine.set_active_symbols(selected_pairs)

    def toggle_trading(self):
        print("✅ Pokrenuto automatsko trgovanje (ili zaustavljeno)")

    def go_home(self):
        print("🏠 Povratak na početni ekran")

    def open_ai_settings(self):
        print("🤖 Otvaranje AI Settings prozora")

    def open_reports(self):
        print("📊 Otvaranje izveštaja")

    def open_live_positions(self):
        print("📈 Otvaranje Live Positions")

    def open_api_news(self):
        print("📰 Otvaranje API and News prozora")

    def open_advanced_settings(self):
        print("⚙️ Otvaranje Advanced Settings")

    def open_general_settings(self):
        print("🔧 Otvaranje General Settings")
