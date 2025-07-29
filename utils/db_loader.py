import os
import sqlite3
import pandas as pd
from logs.logger import log
from datetime import datetime

# Lokacija baze i CSV fajlova
DB_PATH = os.path.join("data", "dukascopy_history.db")
CSV_BASE_DIR = os.path.join("data", "dukascopy")

def create_table_if_not_exists(conn, table_name):
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        timestamp TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    );
    """
    conn.execute(query)
    conn.commit()

def load_csv_to_db(symbol, tf_name):
    table_name = f"{symbol}_{tf_name}".lower()
    file_path = os.path.join(CSV_BASE_DIR, symbol, f"{symbol}_{tf_name}.csv")
    if not os.path.exists(file_path):
        log.warning(f"⚠️ Fajl ne postoji: {file_path}")
        return

    try:
        df = pd.read_csv(file_path)
        if df.empty or "timestamp" not in df.columns:
            log.warning(f"⚠️ CSV fajl je prazan ili nevažeći: {file_path}")
            return

        # Kreiraj folder za bazu ako ne postoji
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        create_table_if_not_exists(conn, table_name)

        # Obriši stare podatke
        conn.execute(f"DELETE FROM {table_name}")
        conn.commit()

        df.to_sql(table_name, conn, if_exists='append', index=False)
        log.info(f"✅ Ubačeno u tabelu {table_name}: {len(df)} redova")
        conn.close()
    except Exception as e:
        log.error(f"❌ Greška prilikom unosa u bazu ({symbol} {tf_name}): {e}")

def load_all_to_db():
    start_time = datetime.now()
    log.info("📦 Učitavam sve CSV fajlove u bazu...")

    if not os.path.exists(CSV_BASE_DIR):
        log.error(f"❌ CSV folder ne postoji: {CSV_BASE_DIR}")
        return

    for symbol in os.listdir(CSV_BASE_DIR):
        symbol_path = os.path.join(CSV_BASE_DIR, symbol)
        if not os.path.isdir(symbol_path):
            continue

        for fname in os.listdir(symbol_path):
            if fname.endswith(".csv") and "_" in fname:
                try:
                    # Popravljeno da podržava simbole sa više _ (npr. EUR_USD_M1)
                    tf_name = fname.split("_")[-1].split(".")[0]
                    load_csv_to_db(symbol, tf_name)
                except Exception as e:
                    log.warning(f"⚠️ Preskačem {fname}: {e}")

    duration = (datetime.now() - start_time).total_seconds()
    log.info(f"🏁 Gotovo sa učitavanjem svih CSV fajlova. Trajanje: {duration:.1f} sekundi")

if __name__ == "__main__":
    load_all_to_db()
