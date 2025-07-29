import os
import pyarrow.parquet as pq

folder_path = r'D:\Izvor-Program\data\dukascopy\parquet_raw'  # Promeni putanju ako treba

def check_parquet_files(path):
    files = [f for f in os.listdir(path) if f.endswith('.parquet')]
    total = len(files)
    print(f"Ukupno .parquet fajlova za proveru: {total}")
    corrupted_files = []

    for i, filename in enumerate(files, 1):
        full_path = os.path.join(path, filename)
        try:
            # Pokušaj da učitaš fajl
            _ = pq.read_table(full_path)
            print(f"[{i}/{total}] OK: {filename}")
        except Exception as e:
            print(f"[{i}/{total}] GREŠKA u fajlu: {filename} -> {e}")
            corrupted_files.append(filename)

    print(f"\nUkupno oštećenih fajlova: {len(corrupted_files)}")
    if corrupted_files:
        print("Lista oštećenih fajlova:")
        for cf in corrupted_files:
            print(f" - {cf}")

if __name__ == "__main__":
    check_parquet_files(folder_path)
