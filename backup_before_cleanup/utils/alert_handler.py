import os
import tkinter.messagebox as msgbox
from datetime import datetime
from logs.logger import log

# Opcionalno: tray notifikacije ako želiš
try:
    from plyer import notification
    HAS_NOTIFICATION = True
except ImportError:
    HAS_NOTIFICATION = False

ALERTS_DIR = os.path.join("alerts")
os.makedirs(ALERTS_DIR, exist_ok=True)

def write_alert_to_file(message: str, level: str = "info"):
    """Upisuje alert u lokalni fajl sa dnevnim logom."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    alert_path = os.path.join(ALERTS_DIR, f"alerts_{today_str}.txt")
    timestamp = datetime.now().strftime('%H:%M:%S')

    try:
        with open(alert_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level.upper()}] {message}\n")
    except Exception as e:
        log.warning(f"⚠️ Ne mogu da upišem alert u fajl: {e}")

def alert(message: str, level: str = "info", show_popup: bool = True, show_tray: bool = False):
    """
    Glavna funkcija za slanje upozorenja.
    - message: tekst upozorenja
    - level: "info", "warning", "error"
    - show_popup: da li prikazati popup kroz GUI
    - show_tray: da li prikazati tray notifikaciju (ako postoji)
    """
    # Log poruka
    if level == "info":
        log.info(message)
    elif level == "warning":
        log.warning(message)
    elif level == "error":
        log.error(message)
    else:
        log.debug(message)

    # Upis u fajl
    write_alert_to_file(message, level)

    # GUI popup
    if show_popup:
        try:
            if level == "error":
                msgbox.showerror("Greška", message)
            elif level == "warning":
                msgbox.showwarning("Upozorenje", message)
            else:
                msgbox.showinfo("Info", message)
        except Exception as e:
            log.warning(f"⚠️ Popup upozorenje nije prikazano: {e}")

    # Tray notifikacija
    if show_tray and HAS_NOTIFICATION:
        try:
            notification.notify(
                title="AI Trgovac - Obaveštenje",
                message=message,
                timeout=5
            )
        except Exception as e:
            log.warning(f"⚠️ Tray notifikacija nije prikazana: {e}")
