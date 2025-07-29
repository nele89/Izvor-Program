import tkinter as tk

class LiveStatsBox:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="📊 Statistika", padx=10, pady=5)
        self.frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.labels = {}
        self.fields = [
            "Otvorene pozicije", 
            "Zatvorene pozicije", 
            "Ukupan profit", 
            "Prosečan profit",
            "Uspešnost (%)"
        ]

        for field in self.fields:
            self._add_field(field)

    def _add_field(self, name):
        field_frame = tk.Frame(self.frame)
        field_frame.pack(anchor="w", pady=2, fill="x")

        label = tk.Label(field_frame, text=f"{name}:", anchor="w", width=20)
        label.pack(side=tk.LEFT)

        value = tk.Label(field_frame, text="...", fg="blue", anchor="w", width=15)
        value.pack(side=tk.LEFT)

        self.labels[name] = value

    def update_stats(self, stats_dict):
        for key, value in stats_dict.items():
            if key in self.labels:
                self.labels[key].config(text=str(value))

    def reset_stats(self):
        for label in self.labels.values():
            label.config(text="...")

    def set_visibility(self, visible=True):
        if visible:
            self.frame.pack(fill="both", expand=True, padx=10, pady=5)
        else:
            self.frame.pack_forget()
