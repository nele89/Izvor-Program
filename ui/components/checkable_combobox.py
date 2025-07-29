from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QCheckBox, QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal


class CheckableComboBox(QComboBox):
    selectionChanged = pyqtSignal(list)  # Signal koji šalje listu izabranih elemenata

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.setModel(QStandardItemModel(self))
        self.setMinimumWidth(200)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._placeholder = "Izaberi valutne parove..."
        self.lineEdit().setPlaceholderText(self._placeholder)
        self.update_display_text()

    def add_check_items(self, items):
        self.model().clear()
        for text in items:
            item = QStandardItem(text)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            self.model().appendRow(item)
        self.update_display_text()

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self.update_display_text()
        self.selectionChanged.emit(self.checked_items())  # Emituj signal kada se promeni izbor

    def checked_items(self):
        return [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]

    def set_checked_items(self, items):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Checked if item.text() in items else Qt.Unchecked)
        self.update_display_text()
        self.selectionChanged.emit(self.checked_items())

    def update_display_text(self):
        selected = self.checked_items()
        self.lineEdit().setText(", ".join(selected) if selected else "")
        if not selected:
            self.lineEdit().setPlaceholderText(self._placeholder)

    def set_placeholder(self, text):
        self._placeholder = text
        self.lineEdit().setPlaceholderText(text)


# Testiranje samostalno ako se pokreće ovaj fajl
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QVBoxLayout(window)

    combo = CheckableComboBox()
    combo.set_placeholder("Odaberi parove")
    combo.add_check_items([
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "USDCAD", "AUDUSD", "NZDUSD", "XAUUSD"
    ])

    def on_selection_changed(selected):
        print(f"✅ Izabrano: {selected}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    window.setWindowTitle("Multi-Select ComboBox")
    window.resize(300, 100)
    window.show()

    sys.exit(app.exec_())
