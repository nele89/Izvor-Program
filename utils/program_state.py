# 🟢 Interna stanja programa

_running = False         # Da li je program aktivno u trejdovanju
_simulation = True       # Da li je aktivan simulacijski mod (default: True)

def set_running_state(state: bool):
    """
    Postavlja stanje programa.
    Ako je state=True, uključuje se pravo trejdovanje i isključuje simulacija.
    Ako je state=False, simulacija se automatski uključuje.
    """
    global _running, _simulation
    _running = state
    _simulation = not state

def is_program_running() -> bool:
    """
    Vrati True ako je aktivno pravo trejdovanje.
    """
    return _running

def is_simulation_mode() -> bool:
    """
    Vrati True ako je program u simulacijskom modu.
    """
    return _simulation

def force_simulation_mode():
    """
    Ručno uključi simulaciju bez obzira na prethodno stanje.
    """
    global _running, _simulation
    _running = False
    _simulation = True

def force_real_trading_mode():
    """
    Ručno uključi pravo trejdovanje bez obzira na prethodno stanje.
    """
    global _running, _simulation
    _running = True
    _simulation = False

def get_mode() -> str:
    """
    Vrati 'real' ako je pravo trejdovanje, 'simulation' ako je simulacija.
    """
    return "real" if _running else "simulation"

# Primer upotrebe:
if __name__ == "__main__":
    print("Trenutni mod:", get_mode())
    set_running_state(True)
    print("Nakon pokretanja trejdovanja:", get_mode())
    set_running_state(False)
    print("Nakon gašenja trejdovanja:", get_mode())
    force_simulation_mode()
    print("Ručno forsirana simulacija:", get_mode())
    force_real_trading_mode()
    print("Ručno forsirano pravo trejdovanje:", get_mode())
