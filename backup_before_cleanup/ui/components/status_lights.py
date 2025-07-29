import tkinter as tk

class StatusLights(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.lights = {}

        self.status_items = {
            "mt5_status": "📡 MT5",
            "ai_training": "🧠 Trening",
            "news_filter": "📰 Vesti",
            "volatility": "📈 Volatilnost",
            "volume": "💹 Volumen"
        }

        for key, label in self.status_items.items():
            frame = tk.Frame(self, padx=5, pady=2)
            frame.pack(side=tk.LEFT)

            color = "gray"
            circle = tk.Canvas(frame, width=20, height=20, bg=self["bg"], highlightthickness=0)
            oval = circle.create_oval(2, 2, 18, 18, fill=color, outline="black")
            circle.pack(side=tk.LEFT)

            text = tk.Label(frame, text=label, font=("Arial", 9))
            text.pack(side=tk.LEFT)

            self.lights[key] = (circle, oval)

    def update_light(self, key, status):
        color_map = {
            "ok": "green",
            "warn": "orange",
            "fail": "red",
            "off": "gray"
        }

        if key in self.lights and status in color_map:
            circle, oval = self.lights[key]
            circle.itemconfig(oval, fill=color_map[status])
