import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from utils.settings_handler import load_settings, save_settings  # koristi pravi handler

class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Podešavanja")
        self.geometry("600x400")

        self.settings = load_settings()
        self.api_entries = []

        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Opšta podešavanja kartica (možeš kasnije proširiti)
        general_frame = ttk.Frame(notebook)
        news_api_frame = ttk.Frame(notebook)

        notebook.add(general_frame, text="Opšta")
        notebook.add(news_api_frame, text="News API ključevi")

        # NEWS API sekcija
        ttk.Label(news_api_frame, text="Unesite do 5 News API ključeva:").pack(pady=5)

        for i in range(5):
            entry = ttk.Entry(news_api_frame, width=60)
            entry.pack(pady=2)
            self.api_entries.append(entry)

        existing_keys = self.settings.get("news_apis", {})
        for i, key in enumerate([
            existing_keys.get("primary", ""),
            existing_keys.get("secondary", ""),
            existing_keys.get("tertiary", ""),
            existing_keys.get("quaternary", ""),
            existing_keys.get("quinary", "")
        ]):
            self.api_entries[i].insert(0, key)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="💾 Sačuvaj", command=self.save_settings).pack()

    def save_settings(self):
        keys = [entry.get().strip() for entry in self.api_entries]

        # Isprazni ključeve koji nisu uneti
        while len(keys) < 5:
            keys.append("")

        self.settings["news_apis"] = {
            "primary": keys[0],
            "secondary": keys[1],
            "tertiary": keys[2],
            "quaternary": keys[3],
            "quinary": keys[4],
        }

        save_settings(self.settings)
        messagebox.showinfo("Uspešno", "API ključevi su sačuvani.")
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    SettingsWindow(master=root)
    root.mainloop()
