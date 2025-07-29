import tkinter as tk
from tkinter import ttk
import MetaTrader5 as mt5
from backend.mt5_connector import get_open_positions, get_account_info
from logs.logger import log

class StatisticsWindow:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.window = tk.Toplevel(self.root)
        self.window.title("Vizuelna statistika trejdovanja")
        self.window.geometry("800x400")
        self.window.configure(bg="#F0F0F0")

        self.tree = ttk.Treeview(
            self.window,
            columns=("symbol", "open", "closed", "profit", "total"),
            show="headings"
        )
        for col in ["symbol", "open", "closed", "profit", "total"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=tk.CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_data()

    def update_data(self):
        try:
            self.tree.delete(*self.tree.get_children())

            # Simboli
            pairs = self.settings.get("pairs", "")
            if isinstance(pairs, str):
                symbols = [s.strip() for s in pairs.split(",") if s.strip()]
            elif isinstance(pairs, list):
                symbols = pairs
            else:
                symbols = [self.settings.get("symbol", "XAUUSD")]

            account_info = get_account_info()
            if not account_info:
                log.warning("⚠️ Nema podataka o računu za statistiku.")
                return

            deals = mt5.history_deals_get()
            if deals is None:
                log.warning("⚠️ Nema istorije trejdova.")
                return

            for sym in symbols:
                open_positions = get_open_positions(sym)
                closed_trades = [d for d in deals if d.symbol == sym]
                closed_count = len(closed_trades)
                profit = sum(d.profit for d in closed_trades)

                self.tree.insert("", "end", values=(
                    sym,
                    len(open_positions),
                    closed_count,
                    f"{profit:.2f}",
                    len(open_positions) + closed_count
                ))

        except Exception as e:
            log.error(f"❌ Greška u update_data statistike: {e}")

        # Automatski refresh svakih 10 sekundi
        self.window.after(10000, self.update_data)
