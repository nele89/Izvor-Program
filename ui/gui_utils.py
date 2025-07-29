# utils/gui_utils.py

from ui.style_config import STYLE
import tkinter as tk
from tkinter import ttk

def apply_style(widget, style_type):
    style_def = STYLE.get(style_type, {})
    
    if isinstance(widget, (tk.Label, ttk.Label)):
        widget.config(
            font=style_def.get("font", ("Segoe UI", 10)),
            foreground=style_def.get("foreground", "black")
        )
    elif isinstance(widget, (tk.Button, ttk.Button)):
        if "bootstyle" in style_def:
            widget.config(bootstyle=style_def["bootstyle"])
        widget.config(
            padding=style_def.get("padding", 5),
            font=style_def.get("font", ("Segoe UI", 10))
        )
    elif isinstance(widget, ttk.Combobox):
        widget.config(
            font=style_def.get("font", ("Segoe UI", 10)),
            width=style_def.get("width", 15)
        )
    elif isinstance(widget, tk.Entry):
        widget.config(
            font=style_def.get("font", ("Segoe UI", 10)),
            width=style_def.get("width", 15)
        )
    elif isinstance(widget, ttk.Treeview):
        # Treeview styling je kompleksniji – možeš koristiti ttk.Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        font=style_def.get("font", ("Segoe UI", 9)),
                        rowheight=style_def.get("rowheight", 22))
        widget.config(style="Custom.Treeview")
    elif isinstance(widget, tk.Frame):
        widget.config(padx=style_def.get("padding", 10), pady=style_def.get("padding", 10))

def apply_theme(window, theme="light"):
    colors = STYLE.get("theme_colors", {}).get(theme, {})
    window.config(bg=colors.get("bg", "#F0F0F0"))
    for widget in window.winfo_children():
        try:
            widget.config(bg=colors.get("bg"), fg=colors.get("fg"))
        except:
            pass  # Nisu svi widgeti podržani
