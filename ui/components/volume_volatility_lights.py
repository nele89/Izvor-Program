import tkinter as tk

class VolumeVolatilityLights(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padx=8, pady=6)

        # Volume light
        tk.Label(self, text="🔊 Volume:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=4)
        self.volume_state = tk.Label(self, text="N/A", bg="gray", fg="white", width=8, font=("Arial", 10, "bold"))
        self.volume_state.grid(row=0, column=1, padx=5)

        # Volatility light
        tk.Label(self, text="📈 Volatility:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=4)
        self.vola_state = tk.Label(self, text="N/A", bg="gray", fg="white", width=8, font=("Arial", 10, "bold"))
        self.vola_state.grid(row=1, column=1, padx=5)

    def update_states(self, volume_level, vola_level):
        """
        volume_level: str ("low", "medium", "high")
        vola_level: str ("low", "medium", "high")
        """
        for label, level in [(self.volume_state, volume_level), (self.vola_state, vola_level)]:
            if level == "low":
                label.config(text="LOW", bg="green")
            elif level == "medium":
                label.config(text="MEDIUM", bg="goldenrod")
            elif level == "high":
                label.config(text="HIGH", bg="red")
            else:
                label.config(text="N/A", bg="gray")

# Primer testiranja samostalno:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Volume & Volatility Lights")
    lights = VolumeVolatilityLights(root)
    lights.pack(padx=20, pady=20)

    # Demo update
    def cycle():
        import random
        choices = ["low", "medium", "high", "N/A"]
        lights.update_states(random.choice(choices), random.choice(choices))
        root.after(1000, cycle)
    cycle()

    root.mainloop()
