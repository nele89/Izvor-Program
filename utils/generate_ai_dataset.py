import os
import pandas as pd
import glob
import ta  # pip install ta

SYMBOL = "XAUUSD"
INPUT_FOLDER = f"data/converted_data/{SYMBOL}/"
OUTPUT_DATASET = "data/trade_features.parquet"   # <--- koristi baš ovo ime

def generate_label(row):
    # BUY (1) kad je EMA10 > EMA30, SELL (0) kad je EMA10 < EMA30
    return 1 if row["ema10"] > row["ema30"] else 0

def process_file(file_path):
    print(f"Obrađujem fajl: {file_path}")
    try:
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            print(f"Preskačem fajl (nepoznat format): {file_path}")
            return None
    except Exception as e:
        print(f"Ne mogu da učitam fajl: {file_path}. Greška: {e}")
        return None

    # Ispravi imena kolona na mala slova
    df.columns = [col.lower() for col in df.columns]

    # Proveri da li postoje potrebne kolone
    for col in ["close", "volume"]:
        if col not in df.columns:
            print(f"⚠️ Fajl {file_path} nema potrebnu kolonu: {col}")
            return None

    # Dodaj indikatore (na osnovu close cene)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    df["ema10"] = ta.trend.ema_indicator(df["close"], window=10)
    df["ema30"] = ta.trend.ema_indicator(df["close"], window=30)
    df["macd"] = ta.trend.macd(df["close"])
    df["spread"] = 0

    # Label po tvojoj strategiji
    df["label"] = df.apply(generate_label, axis=1)

    ai_cols = [
        "rsi", "macd", "ema10", "ema30", "close", "volume", "spread", "label"
    ]
    df = df.dropna(subset=ai_cols)
    df = df[ai_cols]

    return df

def main():
    all_files = glob.glob(os.path.join(INPUT_FOLDER, "**", "*.csv"), recursive=True) \
              + glob.glob(os.path.join(INPUT_FOLDER, "**", "*.xlsx"), recursive=True)

    all_dfs = []
    for file_path in all_files:
        ai_df = process_file(file_path)
        if ai_df is not None:
            all_dfs.append(ai_df)

    if not all_dfs:
        print("Nema validnih podataka za generisanje AI skupa!")
        return

    full_ai_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Ukupno zapisa u datasetu: {len(full_ai_df)}")
    os.makedirs(os.path.dirname(OUTPUT_DATASET), exist_ok=True)
    full_ai_df.to_parquet(OUTPUT_DATASET, index=False)
    print(f"✅ AI dataset sačuvan kao Parquet u {OUTPUT_DATASET}")

if __name__ == "__main__":
    main()
