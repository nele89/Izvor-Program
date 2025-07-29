from tkinter import Frame, Label
from logs.logger import log

LABEL_COLORS = {
    0: ("SELL", "red"),
    1: ("HOLD", "yellow"),
    2: ("BUY", "green"),
    None: ("N/A", "gray")
}

class SignalStatus(Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.label = Label(self, text="AI Signal: N/A", bg="gray", fg="white", font=("Arial", 12, "bold"))
        self.label.pack(padx=5, pady=5)

    def update_signal(self, signal):
        try:
            text, color = LABEL_COLORS.get(signal, ("N/A", "gray"))
            self.label.config(text=f"AI Signal: {text}", bg=color)
            log.info(f"🖥️ SignalStatus ažuriran: {text} ({signal})")
        except Exception as e:
            log.error(f"❌ Greška u update_signal: {e}")
