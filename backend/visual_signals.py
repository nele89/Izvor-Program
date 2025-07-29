from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class SignalIndicator(QLabel):
    def __init__(self, label_text="Status", parent=None):
        super(SignalIndicator, self).__init__(parent)
        self.setText(label_text)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(25)
        self.setStyleSheet("background-color: grey; color: white; border-radius: 5px;")

    def set_status(self, status):
        status = status.lower()
        if status == "active":
            self.setStyleSheet("background-color: green; color: white; border-radius: 5px;")
            self.setText("Aktivno")
        elif status == "paused":
            self.setStyleSheet("background-color: orange; color: black; border-radius: 5px;")
            self.setText("Pauzirano")
        elif status == "error":
            self.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
            self.setText("Greška")
        elif status == "news":
            self.setStyleSheet("background-color: crimson; color: white; border-radius: 5px;")
            self.setText("Negativne vesti")
        else:
            self.setStyleSheet("background-color: grey; color: white; border-radius: 5px;")
            self.setText("Nepoznato")
