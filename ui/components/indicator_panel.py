import tkinter as tk
from tkinter import ttk

class IndicatorPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(borderwidth=1, relief="solid", padx=5, pady=5)

        # Naslov
        title = tk.Label(self, text="📊 Indikatori", font=("Arial", 10, "bold"))
        title.pack(pady=(0, 5))

        # Tabela za prikaz indikatora
        self.table = ttk.Treeview(self, columns=("name", "value"), show="headings", height=8)
        self.table.heading("name", text="Indikator")
        self.table.heading("value", text="Vrednost")
        self.table.column("name", width=120, anchor="w")
        self.table.column("value", width=80, anchor="center")
        self.table.pack(fill="both", expand=True)

    def update_values(self, indicators: dict):
        """Ažurira prikaz indikatora u tabeli."""
        self.table.delete(*self.table.get_children())

        for name, value in indicators.items():
            try:
                val = f"{float(value):.2f}"
            except Exception:
                val = str(value)
            self.table.insert("", "end", values=(name, val))

    def reset(self):
        """Briše sve prikazane indikatore."""
        self.table.delete(*self.table.get_children())
