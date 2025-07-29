from ai.trainer import start_ai_training
from utils.db_manager import get_training_data
from logs.logger import log

def prepare_training_data():
    """
    Učitaj i pripremi podatke za trening AI modela.
    Možeš ovde dodati sve transformacije i čišćenje ako je potrebno.
    """
    df = get_training_data()
    if df is None or df.empty:
        log.warning("⚠️ Nema podataka za trening.")
        return None

    # Ovde možeš dodatno obrađivati df ako treba

    return df

def start_training_if_needed():
    log.info("Pokretanje AI treninga...")
    start_ai_training()
