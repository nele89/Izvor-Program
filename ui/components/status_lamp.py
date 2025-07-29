import tkinter as tk

class StatusLamp(tk.Label):
    def __init__(self, parent, color="gray", text="", **kwargs):
        super().__init__(parent, text=text, bg=color, width=10, padx=5, pady=5, **kwargs)
        self.default_color = color

    def set_color(self, color):
        self.config(bg=color)

    def reset(self):
        self.config(bg=self.default_color)
