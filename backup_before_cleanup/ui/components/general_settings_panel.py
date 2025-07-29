import tkinter as tk
from tkinter import ttk, messagebox
from utils.settings_handler import load_settings, save_settings

class GeneralSettingsPanel(tk.Frame):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.settings = load_settings()
        self.build_ui()
        self.populate_fields()

    def build_ui(self):
        row = 0

        tk.Label(self, text="⏰ Početak radnog vremena:").grid(row=row, column=0, sticky="w", pady=3)
        self.start_hour_var = tk.StringVar()
        tk.Entry(self, textvariable=self.start_hour_var, width=10).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="⏰ Kraj radnog vremena:").grid(row=row, column=0, sticky="w", pady=3)
        self.end_hour_var = tk.StringVar()
        tk.Entry(self, textvariable=self.end_hour_var, width=10).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="🎨 Tema (Light/Dark):").grid(row=row, column=0, sticky="w", pady=3)
        self.theme_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.theme_var, values=["light", "dark"], width=8, state="readonly").grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="🌐 Jezik:").grid(row=row, column=0, sticky="w", pady=3)
        self.language_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.language_var, values=["sr", "en"], width=8, state="readonly").grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="⚡ Min. provera/sek:").grid(row=row, column=0, sticky="w", pady=3)
        self.checks_var = tk.StringVar()
        tk.Entry(self, textvariable=self.checks_var, width=6).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="🔄 Auto restart MT5:").grid(row=row, column=0, sticky="w", pady=3)
        self.restart_var = tk.BooleanVar()
        tk.Checkbutton(self, variable=self.restart_var).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        tk.Label(self, text="⚡ Scalping mod:").grid(row=row, column=0, sticky="w", pady=3)
        self.scalping_var = tk.BooleanVar()
        tk.Checkbutton(self, variable=self.scalping_var).grid(row=row, column=1, sticky="w", padx=5)
        row += 1

        # Dugme za snimanje
        tk.Button(self, text="💾 Sačuvaj podešavanja", command=self.save).grid(row=row, column=0, columnspan=2, pady=12)

    def populate_fields(self):
        self.start_hour_var.set(self.settings.get("start_hour", "08:00"))
        self.end_hour_var.set(self.settings.get("end_hour", "20:00"))
        self.theme_var.set(self.settings.get("theme", "light"))
        self.language_var.set(self.settings.get("language", "sr"))
        self.checks_var.set(str(self.settings.get("min_checks_per_second", 5)))
        self.restart_var.set(self.settings.get("restart_mt5_on_crash", "yes") == "yes")
        self.scalping_var.set(self.settings.get("scalping_mode", "no") == "yes")

    def save(self):
        # Priprema za snimanje
        self.settings["start_hour"] = self.start_hour_var.get()
        self.settings["end_hour"] = self.end_hour_var.get()
        self.settings["theme"] = self.theme_var.get()
        self.settings["language"] = self.language_var.get()
        self.settings["min_checks_per_second"] = int(self.checks_var.get())
        self.settings["restart_mt5_on_crash"] = "yes" if self.restart_var.get() else "no"
        self.settings["scalping_mode"] = "yes" if self.scalping_var.get() else "no"

        try:
            save_settings(self.settings)
            if self.on_save:
                self.on_save()
            messagebox.showinfo("Uspeh", "Podešavanja su sačuvana!")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu da sačuvam podešavanja: {e}")

# Primer upotrebe:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("General Settings Panel")
    panel = GeneralSettingsPanel(root)
    panel.pack(padx=15, pady=15)
    root.mainloop()
