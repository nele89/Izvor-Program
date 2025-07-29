import tkinter as tk
from tkinter import ttk
from utils.db_manager import get_all_decisions

class DecisionMemoryWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("AI Decision Memory")
        self.window.geometry("700x400")

        self.tree = ttk.Treeview(self.window, columns=("timestamp", "symbol", "decision", "explanation", "result"), show="headings")
        self.tree.heading("timestamp", text="Vreme")
        self.tree.heading("symbol", text="Simbol")
        self.tree.heading("decision", text="Odluka")
        self.tree.heading("explanation", text="Objašnjenje")
        self.tree.heading("result", text="Ishod")

        self.tree.column("timestamp", width=120)
        self.tree.column("symbol", width=80)
        self.tree.column("decision", width=80)
        self.tree.column("explanation", width=300)
        self.tree.column("result", width=100)

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.load_data()

    def load_data(self):
        odluke = get_all_decisions()
        for d in odluke:
            self.tree.insert("", tk.END, values=(d[1], d[2], d[3], d[4], d[5]))
