import tkinter as tk
from tkinter import ttk
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from logs.logger import log

class ClosedPositionsWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Zatvorene pozicije")
        self.window.geometry("850x500")
        self.window.configure(bg="#F0F0F0")

        self.symbol_filter = tk.StringVar()
        self.sort_order = tk.StringVar(value="descending")

        self.build_ui()
        self.populate_positions()

    def build_ui(self):
        top_frame = tk.Frame(self.window, bg="#F0F0F0")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Simbol:", bg="#F0F0F0").pack(side=tk.LEFT)
        entry = tk.Entry(top_frame, textvariable=self.symbol_filter, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        entry.bind("<Return>", lambda e: self.populate_positions())

        sort_btn = tk.Button(top_frame, text="Sortiraj po profitu", command=self.sort_by_profit)
        sort_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(top_frame, text="Osveži", command=self.populate_positions)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(
            self.window,
            columns=("symbol", "type", "volume", "profit", "open_time", "close_time"),
            show="headings"
        )

        for col in ["symbol", "type", "volume", "profit", "open_time", "close_time"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=tk.CENTER, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def populate_positions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)

        deals = mt5.history_deals_get(start_time, end_time)
        if deals is None:
            log.error("❌ Ne mogu da dohvatim zatvorene pozicije.")
            return

        symbol_filter = self.symbol_filter.get().strip().upper()
        count = 0

        for d in deals:
            if d.type not in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                continue
            if symbol_filter and d.symbol.upper() != symbol_filter:
                continue

            open_time = datetime.fromtimestamp(d.time).strftime("%Y-%m-%d %H:%M:%S") if hasattr(d, "time") else "-"
            close_time = datetime.fromtimestamp(d.time_msc / 1000).strftime("%Y-%m-%d %H:%M:%S") if hasattr(d, "time_msc") else "-"

            self.tree.insert("", "end", values=(
                d.symbol,
                "BUY" if d.type == mt5.DEAL_TYPE_BUY else "SELL",
                d.volume,
                f"{d.profit:.2f}",
                open_time,
                close_time
            ))
            count += 1

        if count == 0:
            log.info("ℹ️ Nema zatvorenih pozicija za prikaz.")

    def sort_by_profit(self):
        children = self.tree.get_children()
        sorted_items = sorted(
            children,
            key=lambda i: float(self.tree.item(i, "values")[3]),
            reverse=self.sort_order.get() == "descending"
        )
        for i in children:
            self.tree.detach(i)
        for i in sorted_items:
            self.tree.move(i, '', 'end')

        self.sort_order.set("ascending" if self.sort_order.get() == "descending" else "descending")
