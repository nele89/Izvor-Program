import threading
from tools.csv_to_parquet_batch import convert_all_csv_to_parquet
from tools.parquet_merge import merge_all_parquet
from tools.parquet_resample import resample_parquet_all

conversion_lock = threading.Lock()

def conversion_manager(force=False):
    if conversion_lock.locked():
        print("🔄 Konverzija je već u toku. Ignorišem novi zahtev.")
        return
    with conversion_lock:
        print("🚀 Pokrećem proces konverzije i spajanja podataka...")
        try:
            convert_all_csv_to_parquet()
            merge_all_parquet()
            resample_parquet_all()
            print("✅ Konverzija i obrada uspešno završeni.")
        except Exception as e:
            print(f"❌ Greška u conversion_manager-u: {e}")
