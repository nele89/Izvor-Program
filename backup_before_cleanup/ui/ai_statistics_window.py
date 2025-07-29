import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.db_manager import get_all_decisions

class AIStatisticsWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("AI Statistika")
        self.window.geometry("600x450")
        self.window.configure(bg="#F0F0F0")

        self.top_frame = tk.Frame(self.window, bg="#F0F0F0")
        self.top_frame.pack(pady=10)

        self.chart_frame = tk.Frame(self.window, bg="#F0F0F0")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.show_chart()

    def show_chart(self):
        decisions = get_all_decisions()

        total = len(decisions)
        wins = sum(1 for d in decisions if d[5] == "win")
        losses = sum(1 for d in decisions if d[5] == "loss")
        pending = total - wins - losses

        win_rate = (wins / total) * 100 if total > 0 else 0

        # Prikaz teksta
        summary = f"Ukupno: {total} | Pobedničkih: {wins} | Gubitničkih: {losses} | Pending: {pending} | Win Rate: {win_rate:.2f}%"
        tk.Label(self.top_frame, text=summary, font=("Segoe UI", 10, "bold"), bg="#F0F0F0").pack()

        # Bar chart
        labels = ["WIN", "LOSS", "PENDING"]
        values = [wins, losses, pending]
        colors = ["green", "red", "gray"]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, values, color=colors)
        ax.set_title("AI Predikcije - Statistika")
        ax.set_ylabel("Broj odluka")
        ax.set_ylim(0, max(values) + 5 if values else 5)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
