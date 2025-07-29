from PyQt5 import QtWidgets
from ui.components.checkable_combobox import CheckableComboBox # 👈 Obavezno da postoji fajl checkable_combobox.py

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setWindowTitle('AI Settings')
        self.layout = QtWidgets.QVBoxLayout(Form)

        self.MainWindow = QtWidgets.QMainWindow(Form)
        self.layout.addWidget(self.MainWindow)

        self.centralwidget = QtWidgets.QWidget(Form)
        self.layout.addWidget(self.centralwidget)

        self.btnHome = QtWidgets.QPushButton("Home", Form)
        self.layout.addWidget(self.btnHome)

        self.btnAISettings = QtWidgets.QPushButton("AI Settings", Form)
        self.layout.addWidget(self.btnAISettings)

        self.btnReports = QtWidgets.QPushButton("Reports", Form)
        self.layout.addWidget(self.btnReports)

        self.btnLivePositions = QtWidgets.QPushButton("Live Positions", Form)
        self.layout.addWidget(self.btnLivePositions)

        self.btnApiNews = QtWidgets.QPushButton("API and News", Form)
        self.layout.addWidget(self.btnApiNews)

        self.menuAdvancedWindowButton = QtWidgets.QPushButton("Advanced", Form)
        self.layout.addWidget(self.menuAdvancedWindowButton)

        # 👇 Multi-select dropdown umesto običnog
        self.dropdownPairSelector = CheckableComboBox(Form)
        self.dropdownPairSelector.add_check_items([
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "USDCAD", "AUDUSD", "NZDUSD", "XAUUSD"
        ])
        self.layout.addWidget(self.dropdownPairSelector)

        self.menuGeneralSettingsButton = QtWidgets.QPushButton("General Settings", Form)
        self.layout.addWidget(self.menuGeneralSettingsButton)

        self.lampSell = QtWidgets.QLabel("🔴 SELL", Form)
        self.layout.addWidget(self.lampSell)

        self.startStopButton = QtWidgets.QPushButton("Start/Stop", Form)
        self.layout.addWidget(self.startStopButton)

        self.lampBuy = QtWidgets.QLabel("🟢 BUY", Form)
        self.layout.addWidget(self.lampBuy)

        self.labelVolatility = QtWidgets.QLabel("Volatility:", Form)
        self.layout.addWidget(self.labelVolatility)

        self.volatilityLampLow = QtWidgets.QLabel("🟢", Form)
        self.layout.addWidget(self.volatilityLampLow)

        self.volatilityLampMed = QtWidgets.QLabel("🟡", Form)
        self.layout.addWidget(self.volatilityLampMed)

        self.volatilityLampHigh = QtWidgets.QLabel("🔴", Form)
        self.layout.addWidget(self.volatilityLampHigh)

        self.labelVolume = QtWidgets.QLabel("Volume:", Form)
        self.layout.addWidget(self.labelVolume)

        self.volumeLampLow = QtWidgets.QLabel("🟦", Form)
        self.layout.addWidget(self.volumeLampLow)

        self.volumeLampMed = QtWidgets.QLabel("🟨", Form)
        self.layout.addWidget(self.volumeLampMed)

        self.volumeLampHigh = QtWidgets.QLabel("🟧", Form)
        self.layout.addWidget(self.volumeLampHigh)

        self.labelNews = QtWidgets.QLabel("News Status:", Form)
        self.layout.addWidget(self.labelNews)

        self.newsStatusLamp = QtWidgets.QLabel("🔴", Form)
        self.layout.addWidget(self.newsStatusLamp)

        self.labelBalance = QtWidgets.QLabel("Balance: 12,850.00 USD", Form)
        self.layout.addWidget(self.labelBalance)

        self.labelProfit = QtWidgets.QLabel("Total Profit: +1,120.75 USD", Form)
        self.layout.addWidget(self.labelProfit)

        self.labelTrades = QtWidgets.QLabel("Total Trades: 32", Form)
        self.layout.addWidget(self.labelTrades)

        self.labelWinRate = QtWidgets.QLabel("Win Rate: 75%", Form)
        self.layout.addWidget(self.labelWinRate)

        self.labelDrawdown = QtWidgets.QLabel("Drawdown: -3.2%", Form)
        self.layout.addWidget(self.labelDrawdown)

        self.labelAvgTime = QtWidgets.QLabel("Avg. Trade Time: 02m 40s", Form)
        self.layout.addWidget(self.labelAvgTime)

        self.menubar = QtWidgets.QMenuBar(Form)
        self.layout.addWidget(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(Form)
        self.layout.addWidget(self.statusbar)
