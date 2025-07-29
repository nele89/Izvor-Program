import os
import pandas as pd

output_dir = 'data/converted'

for timeframe in ['M1', 'M5', 'H1']:
    out_path = os.path.join(output_dir, f"XAUUSD_{timeframe}.csv")
    if os.path.exists(out_path):
        os.remove(out_path)

for timeframe in ['M1', 'M5', 'H1']:
    batch_files = [f for f in os.listdir(output_dir)
                   if f.startswith(f"XAUUSD_{timeframe}_batch") and f.endswith('.csv')]
    batch_files.sort()
    if not batch_files:
        print(f"[INFO] Nema batch fajlova za timeframe {timeframe}")
        continue
    print(f"[INFO] Spajam {len(batch_files)} batch fajlova za {timeframe}:")
    dfs = []
    for f in batch_files:
        path = os.path.join(output_dir, f)
        print(f"    Učitavam: {f}")
        df = pd.read_csv(path)
        dfs.append(df)
    full_df = pd.concat(dfs, ignore_index=True)
    if 'time' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['time'])
    out_path = os.path.join(output_dir, f"XAUUSD_{timeframe}.csv")
    full_df.to_csv(out_path, index=False)
    print(f"[INFO] Spojen fajl: {out_path} ({len(full_df)} redova)")

print("[INFO] Završeno spajanje svih batch fajlova.")
