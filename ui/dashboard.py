import os
import sys
import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

from dotenv import load_dotenv

from logs.logger import log
from ui.screens.live_position import LivePositionWindow
from ui.helpers.refresh_manager import RefreshManager

from utils.news_state import get_latest_sentiment, get_news_pause_state
from utils.trading_control import is_trading_paused
from utils.model_predictor import predict_trade
from utils.db_manager import insert_decision
from utils.indicator_data import get_live_indicators
from strategy.strategy_scheduler import start_strategy_scheduler, stop_strategy_scheduler
from ai.trainer import manual_train_full_model, ai_training_in_progress
from utils.settings_handler import save_settings

SYMBOL = "XAUUSD"

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or {}

        # Dodaj try-except blok za jasnu dijagnostiku .ui problema
        try:
            uic.loadUi(os.path.join("ui", "dashboard.ui"), self)
        except Exception as e:
            import traceback
            print("==== UI LOAD FAIL ====")
            print(e)
            traceback.print_exc()
            raise

        self.setWindowTitle(f"Izvor 1.1.1.1 – MODE: {self.settings.get('mode','scalping').upper()}")

        # Povezivanje dugmadi
        self.btnStart.clicked.connect(self.toggle_trading)
        self.btnAIPrediction.clicked.connect(self.show_ai_prediction)
        self.btnExitAll.clicked.connect(self.on_close_all)
        self.btnHome.clicked.connect(self.show_home)
        self.btnStatistics.clicked.connect(self.show_statistics)
        self.btnClosedPositions.clicked.connect(self.show_closed_positions)
        self.btnSettings.clicked.connect(self.show_settings)
        self.btnLivePositions.clicked.connect(self.otvori_live_pozicije)
        self.btnAITrain.clicked.connect(self.manual_ai_train)
        self.btnRefresh.clicked.connect(self.force_refresh)

        # ComboBox za mod
        self.comboMode.clear()
        self.comboMode.addItems(["scalping", "daily"])
        curr_mode = self.settings.get("mode", "scalping").lower()
        idx = self.comboMode.findText(curr_mode)
        if idx >= 0:
            self.comboMode.setCurrentIndex(idx)
        self.comboMode.currentTextChanged.connect(self.on_mode_changed)
        self.lblCurrentMode.setText(f"Trenutni mod: {self.settings.get('mode', 'scalping').capitalize()}")

        # Timer za AI Train dugme
        self.ai_train_timer = QTimer(self)
        self.ai_train_timer.setInterval(2000)
        self.ai_train_timer.timeout.connect(self._update_ai_train_btn)
        self.ai_train_timer.start()

        # Stub-funkcije za menije
        self.show_home = lambda: None
        self.show_statistics = lambda: None
        self.show_closed_positions = lambda: None
        self.show_settings = lambda: None

        self.refresh_status()
        self.start_refresh_cycle()

    def on_mode_changed(self, new_mode):
        new_mode = new_mode.lower()
        if new_mode not in ["scalping", "daily"]:
            return
        self.settings["mode"] = new_mode
        save_settings(self.settings)
        self.lblCurrentMode.setText(f"Trenutni mod: {new_mode.capitalize()}")
        self.setWindowTitle(f"Izvor 1.1.1.1 – MODE: {new_mode.upper()}")
        log.info(f"✅ PROMENJEN MOD: {new_mode}")
        QtWidgets.QMessageBox.information(self, "Promena moda", f"Mod je promenjen u: {new_mode.upper()}")

    def update_progress_bar(self, step_name, value):
        self.progressBar.setValue(value)
        self.progressBar.setFormat(f"{step_name}... {value}%")
        if value == 100:
            self.progressBar.setFormat("✅ Priprema završena!")

    def manual_ai_train(self):
        if ai_training_in_progress:
            self.lblAIPrediction.setText("AI trening već u toku...")
            return
        self.lblAIPrediction.setText("Pokrenut AI trening (ručno)...")
        manual_train_full_model()

    def _update_ai_train_btn(self):
        self.btnAITrain.setEnabled(not ai_training_in_progress)
        self.btnAITrain.setText("AI Trening: U TOKU" if ai_training_in_progress else "Pokreni AI Trening")

    def _set_label_colored(self, label, text, color):
        label.setText(text)
        label.setStyleSheet(f"color: {color}; font-weight: bold")

    def refresh_status(self):
        try:
            sentiment = get_latest_sentiment()
            paused = is_trading_paused() or get_news_pause_state()
            # Glavna signal labela – jasan status i boja
            if paused and sentiment in ("panic", "fear"):
                self._set_label_colored(self.lblSignal, "Vesti su negativne", "red")
            elif not paused and sentiment in ("positive", "neutral"):
                self._set_label_colored(self.lblSignal, "Vesti su pozitivne", "green")
            elif sentiment == "ignore":
                self._set_label_colored(self.lblSignal, "Nema uticaja (ignore)", "gray")
            else:
                self._set_label_colored(self.lblSignal, "Status nepoznat", "black")
            sentiment_text = {
                "positive": "Sentiment: POZITIVAN",
                "neutral": "Sentiment: NEUTRALAN",
                "panic": "Sentiment: PANIKA",
                "fear": "Sentiment: STRAH",
                "ignore": "Sentiment: IGNORE",
            }.get(sentiment, f"Sentiment: {sentiment.upper()}")
            self.lblNewsSentiment.setText(sentiment_text)
            if paused:
                self._set_label_colored(self.lblTradingStatus, "Pauzirano", "red")
            else:
                self._set_label_colored(self.lblTradingStatus, "Aktivno", "green")
        except Exception as e:
            log.error(f"Greška u refresh_status: {e}")

    def fetch_news(self):
        try:
            news_apis = self.settings.get("news_apis", {})
            url = (
                news_apis.get("primary") or
                news_apis.get("secondary") or
                ""
            )
            if not url:
                load_dotenv()
                finnhub_api_key = os.getenv("FINNHUB_API_KEY")
                marketaux_api_key = os.getenv("MARKETAUX_API_KEY")
                if finnhub_api_key:
                    url = f"https://finnhub.io/api/v1/news?category=general&token={finnhub_api_key}"
                elif marketaux_api_key:
                    url = f"https://api.marketaux.com/v1/news/all?api_token={marketaux_api_key}"

            if not url:
                self.lblNews.setText("⚠️ Nije podešen API za vesti.")
                return

            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                msg = f"⚠️ API greška ({resp.status_code})"
                self.lblNews.setText(msg)
                log.warning(msg + f" (url: {url})")
                return

            data = resp.json()
            if "finnhub" in url or ("news" in url and "token=" in url):
                if isinstance(data, list) and data:
                    title = data[0].get("headline") or data[0].get("title", "")
                    self.lblNews.setText(title or "⚠️ Nema naslova vesti.")
                else:
                    self.lblNews.setText("⚠️ Nema dostupnih vesti.")
            elif "marketaux" in url:
                if isinstance(data, dict) and "data" in data and data["data"]:
                    title = data["data"][0].get("title", "")
                    self.lblNews.setText(title or "⚠️ Nema naslova vesti.")
                else:
                    self.lblNews.setText("⚠️ Nema dostupnih vesti.")
            else:
                self.lblNews.setText("⚠️ Nepodržan API format.")
                log.warning(f"API response neprepoznat (url: {url})")

        except Exception as e:
            log.error(f"Greška pri učitavanju vesti: {e}")
            self.lblNews.setText("⚠️ Ne mogu da učitam vesti.")

    def show_ai_prediction(self):
        try:
            symbol = self.settings.get("symbol", SYMBOL)
            indicator_data = get_live_indicators(symbol)
            if not indicator_data:
                self.lblAIPrediction.setText("AI: N/A")
                return
            features_needed = [
                "rsi", "macd", "ema10", "ema30", "close", "volume",
                "spread", "adx", "stochastic", "cci", "gold_trend"
            ]
            input_data = {k: indicator_data.get(k, None) for k in features_needed}
            if None in input_data.values():
                self.lblAIPrediction.setText("AI: N/A (feature mismatch)")
                log.error(f"❌ Nedostaju feature-i za predikciju: {input_data}")
                return
            current_mode = self.settings.get("mode", "scalping")
            decision = predict_trade(mode=current_mode, **input_data)
            if not isinstance(decision, str) or decision == "N/A":
                self.lblAIPrediction.setText("AI: N/A")
            else:
                self.lblAIPrediction.setText(f"AI: {decision.upper()}")
                if self.settings.get("ai_use_decision_memory", True):
                    explanation = ", ".join([f"{k}={v}" for k, v in input_data.items()])
                    insert_decision(symbol, decision.lower(), explanation, result="pending")
        except Exception as e:
            log.error(f"Greška u AI predikciji: {e}")
            self.lblAIPrediction.setText("AI: Greška")

    def toggle_trading(self):
        from utils.program_state import is_program_running, set_running_state
        running = is_program_running()
        set_running_state(not running)
        if not running:
            start_strategy_scheduler()
            self._set_label_colored(self.lblTradingStatus, "Aktivno", "green")
            log.info("✅ Program je POKRENUT")
        else:
            stop_strategy_scheduler()
            self._set_label_colored(self.lblTradingStatus, "Pauzirano", "red")
            log.info("⏸️ Program je ZAUSTAVLJEN")

    def on_close_all(self):
        from backend.mt5_connector import close_all_positions
        reply = QtWidgets.QMessageBox.question(
            self,
            "Zatvori sve pozicije",
            "Da li ste sigurni da želite da zatvorite SVE pozicije?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            close_all_positions()
            log.info("✔️ Sve pozicije zatvorene na zahtev korisnika.")
            QtWidgets.QMessageBox.information(self, "Zatvoreno", "Sve pozicije su zatvorene.")

    def otvori_live_pozicije(self):
        prozor = LivePositionWindow(symbol=SYMBOL)
        prozor.exec_()

    def start_refresh_cycle(self):
        self.refresh = RefreshManager(interval_ms=5000)
        self.refresh.register_callback(self.refresh_status)
        self.refresh.register_callback(self.fetch_news)
        self.refresh.register_callback(self.show_ai_prediction)
        self.refresh.start()

    def force_refresh(self):
        self.refresh_status()
        self.fetch_news()
        self.show_ai_prediction()

def launch_ui(settings):
    app = QtWidgets.QApplication(sys.argv)
    window = DashboardWindow(settings)
    window.show()
    sys.exit(app.exec_())
