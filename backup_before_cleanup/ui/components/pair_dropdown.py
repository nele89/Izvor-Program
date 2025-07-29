import tkinter as tk
from tkinter import ttk

class PairDropdown:
    def __init__(self, parent, pairs, on_select):
        self.parent = parent
        self.on_select = on_select
        self.pairs = pairs

        self.label = tk.Label(parent, text="Izaberi simbol:", font=("Arial", 10))
        self.label.pack(side=tk.LEFT, padx=5)

        self.combo = ttk.Combobox(parent, values=pairs, state="readonly")
        self.combo.current(0)
        self.combo.pack(side=tk.LEFT, padx=5)
        self.combo.bind("<<ComboboxSelected>>", self.selection_changed)

    def selection_changed(self, event):
        selected_symbol = self.combo.get()
        self.on_select(selected_symbol)

    def get_selected(self):
        return self.combo.get()
