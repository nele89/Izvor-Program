# 📁 ui/signal_status.py

from logs.logger import log  # ✅ ako želiš da beležiš promene statusa

# ✅ Ove promenljive su samo stringovi
signal_status_callback = None
signal_color = "#CCCC00"  # žuta (neutralno)
signal_text = "NEUTRAL"   # tekst za status

def register_signal_callback(callback):
    """
    Registruje funkciju iz GUI-ja koja se poziva kada se status promeni.
    """
    global signal_status_callback
    signal_status_callback = callback

def update_signal_lamp(color: str, message: str):
    """
    Ažurira signal indikator u GUI-ju preko callback-a.
    Takođe ažurira i globalne vrednosti.
    """
    global signal_color, signal_text
    signal_color = color
    signal_text = message

    log.info(f"💡 Signal lampica ažurirana: {color} – {message}")

    if signal_status_callback:
        try:
            signal_status_callback(color, message)
        except Exception as e:
            log.warning(f"⚠️ Greška u signal callback funkciji: {e}")

def get_current_signal_status():
    """
    Vrati trenutnu boju i poruku signala.
    """
    return signal_color, signal_text
