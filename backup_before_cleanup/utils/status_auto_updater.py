import os
import time
from logs.logger import log

# Možeš ovde dodati i više "status" provera po potrebi:
def check_internet():
    import requests
    try:
        requests.get("https://www.google.com/", timeout=5)
        return True
    except Exception:
        return False

def check_mt5_connection():
    # Ova funkcija je primer - zameni je tvojom stvarnom proverom!
    # npr. iz backend.mt5_connector import is_mt5_connected
    try:
        from backend.mt5_connector import is_mt5_connected
        return is_mt5_connected()
    except Exception:
        return False

def auto_update_status():
    status_report = {}

    # Provera internet konekcije
    net_ok = check_internet()
    status_report["internet"] = "OK" if net_ok else "NE RADI"

    # Provera MT5 konekcije (ako imaš implementirano)
    mt5_ok = check_mt5_connection()
    status_report["mt5"] = "OK" if mt5_ok else "NE RADI"

    # Dodatni statusi (primer: provera da li su folderi dostupni)
    data_dir = os.path.join("data", "dukascopy", "XAUUSD")
    status_report["data_folder"] = "OK" if os.path.exists(data_dir) else "NE POSTOJI"

    # Možeš dodati proveru GUI-ja, baze, API konekcije, rada glavnog procesa itd.

    # Loguj status
    log.info(f"[STATUS] Internet: {status_report['internet']} | MT5: {status_report['mt5']} | Data folder: {status_report['data_folder']}")

    # (Opcionalno: snimi status u status.txt, bazu ili GUI)
    with open("status.txt", "w", encoding="utf-8") as f:
        for k, v in status_report.items():
            f.write(f"{k}: {v}\n")

    # Možeš dodati i povratak statusa kao rečnik, pa koristiti u GUI-ju
    return status_report

if __name__ == "__main__":
    while True:
        auto_update_status()
        time.sleep(30)  # Svakih 30 sekundi za test
