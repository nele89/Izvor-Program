import tkinter as tk
from tkinter import messagebox
from utils.program_state import set_running_state

class StartStopButton:
    def __init__(self, parent, on_start, on_stop):
        self.parent = parent
        self.on_start = on_start
        self.on_stop = on_stop
        self.is_running = False

        self.button = tk.Button(
            parent,
            text="▶ Pokreni",
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.toggle
        )
        self.button.pack(pady=10)

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def start(self):
        try:
            self.on_start()
            self.is_running = True
            set_running_state(True)  # Aktivira pravo trejdovanje, gasi simulaciju
            self.button.config(text="⏹ Zaustavi", bg="red")
        except Exception as e:
            messagebox.showerror("Greška pri pokretanju", str(e))

    def stop(self):
        try:
            self.on_stop()
            self.is_running = False
            set_running_state(False)  # Aktivira simulaciju
            self.button.config(text="▶ Pokreni", bg="green")
        except Exception as e:
            messagebox.showerror("Greška pri zaustavljanju", str(e))
