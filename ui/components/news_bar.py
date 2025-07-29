import tkinter as tk

class NewsBar(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="📰 Ekonomske vesti:", font=("Arial", 10, "bold"))
        self.label.pack(anchor="w")

        self.news_text = tk.StringVar()
        self.news_label = tk.Label(self, textvariable=self.news_text, wraplength=600, justify="left", fg="darkblue")
        self.news_label.pack(anchor="w", padx=5)

    def update_news(self, headline, sentiment=None):
        prefix = ""
        if sentiment == "positive":
            prefix = "📈 "
        elif sentiment == "negative" or sentiment == "fear" or sentiment == "panic":
            prefix = "📉 "
        elif sentiment == "neutral":
            prefix = "➖ "
        self.news_text.set(f"{prefix}{headline}")
