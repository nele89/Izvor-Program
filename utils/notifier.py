import platform
import logging

try:
    if platform.system() == "Windows":
        from win10toast import ToastNotifier
        notifier = ToastNotifier()
    else:
        notifier = None
except ImportError:
    notifier = None

from logs.logger import log


def send_notification(title, message):
    log.info(f"[NOTIFIKACIJA] {title}: {message}")

    if notifier:
        try:
            notifier.show_toast(
                title,
                message,
                duration=5,
                threaded=True,
                icon_path=None  # Možeš dodati .ico fajl ovde ako želiš
            )
        except Exception as e:
            log.warning(f"Tray notifikacija nije uspela: {e}")


def notify_pause_due_to_news():
    send_notification(
        "🚫 Trgovanje pauzirano",
        "Trgovanje je obustavljeno zbog negativnih vesti."
    )


def notify_resume_due_to_news():
    send_notification(
        "✅ Trgovanje nastavljeno",
        "Trgovanje je ponovo aktivno – vesti su pozitivne ili neutralne."
    )


def send_popup_alert(message):
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Upozorenje", message)
        root.destroy()
    except Exception as e:
        logging.warning(f"Popup upozorenje nije moguće prikazati: {e}")
