import tkinter as tk
from tkinter import scrolledtext

class AlertsPanel(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="🔔 Obaveštenja", font=("Arial", 10, "bold"))
        self.label.pack(anchor="w")

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=6, state="disabled", font=("Consolas", 9))
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def append_alert(self, message):
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.configure(state="disabled")
        self.text_area.yview_moveto(1.0)  # Auto-scroll na dno
