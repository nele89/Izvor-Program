import os
import re
import pandas as pd
import time
import datetime
from logs.logger import log

CSV_FILENAME_TEMPLATE = "{symbol}_{year}-{month:02d}-{day:02d}-{hour:02d}.csv"
DATA_START_DATE = datetime.datetime(2025, 7, 2)
DATA_DIR = r"D:\Izvor-Program\data\dukascopy\XAUUSD"
CONVERTED_DIR = r"D:\Izvor-Program\data\converted"
SYMBOL = "XAUUSD"
CHUNKSIZE = 1_000_000  # 1 milion redova

# =========== MODE =========== 
MODE = "scalping"  # ili "daily"
TIMEFRAME_MODES = {
    "scalping": ["M1", "M5", "M15"],
    "daily": ["M15", "M30", "H1"]
}
ALLOWED_TIMEFRAMES = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "M30": "30min",
    "H1": "1h"
}
SELECTED_TIMEFRAMES = [tf for tf in TIMEFRAME_MODES[MODE] if tf in ALLOWED_TIMEFRAMES]

class DataConverter:
    def __init__(self, source_dir=DATA_DIR, output_dir=CONVERTED_DIR):
        self.source_dir = source_dir
        self.output_dir = output_dir
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_existing_files(self):
        return set(f for f in os.listdir(self.source_dir) if f.endswith('.csv'))

    def _expected_filenames(self):
        now = datetime.datetime.utcnow()
        filenames = []
        dt = DATA_START_DATE
        while dt <= now:
            filenames.append(CSV_FILENAME_TEMPLATE.format(
                symbol=SYMBOL,
                year=dt.year, month=dt.month, day=dt.day, hour=dt.hour
            ))
            dt += datetime.timedelta(hours=1)
        return filenames

    def _download_missing_files(self, missing_files):
        for fname in missing_files:
            path = os.path.join(self.source_dir, fname)
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write("time,ask,bid,volume,spread\n")
                log.info(f"Dummy fajl napravljen: {fname}")

    def convert_to_timeframe(self, df, timeframe, index_col='time'):
        if index_col not in df.columns and df.index.name != index_col:
            log.error(f"Kolona {index_col} ne postoji u DataFrame-u!")
            return None

        if df.index.name != index_col:
            df[index_col] = pd.to_datetime(df[index_col])
            df.set_index(index_col, inplace=True)

        df = df.sort_index()

        if timeframe == 'M1':
            df_out = df[['bid', 'ask', 'volume', 'spread']].copy()
            df_out['tick_count'] = 1
        else:
            rule = ALLOWED_TIMEFRAMES[timeframe]
            df_out = df.resample(rule).agg({
                'bid': ['first', 'max', 'min', 'last', 'mean', 'count'],
                'ask': ['mean'],
                'volume': 'sum',
                'spread': 'mean'
            }).dropna()

            df_out.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df_out.columns.values]
            df_out = df_out.rename(columns={
                'bid_first': 'open',
                'bid_max': 'high',
                'bid_min': 'low',
                'bid_last': 'close',
                'bid_mean': 'bid',
                'bid_count': 'tick_count',
                'ask_mean': 'ask'
            })

            df_out['gold_trend'] = df_out['close'].diff().apply(
                lambda x: 'UP' if x > 0 else ('DOWN' if x < 0 else 'FLAT')
            )
        return df_out

    def convert_and_append_new(self, new_files):
        if not new_files:
            return

        for timeframe in SELECTED_TIMEFRAMES:
            out_file = os.path.join(self.output_dir, f"{SYMBOL}_{timeframe}.csv")
            if not os.path.exists(out_file):
                with open(out_file, "w") as f:
                    pass  # prazno

            for file in new_files:
                file_path = os.path.join(self.source_dir, file)
                try:
                    match = re.match(r".*_(\d{4}-\d{2}-\d{2})-(\d{2})\.csv$", file)
                    if not match:
                        log.warning(f"Ne mogu parsirati datum i sat iz imena fajla: {file}")
                        continue
                    date_str, hour_str = match.groups()
                    chunk_iter = pd.read_csv(file_path, chunksize=CHUNKSIZE)

                    for i, chunk in enumerate(chunk_iter):
                        if 'time' not in chunk.columns:
                            log.error(f"Kolona 'time' ne postoji u {file_path}!")
                            continue

                        def formiraj_time(row):
                            t = str(row['time'])
                            if ':' in t:
                                parts = t.split(':')
                                if len(parts) == 2:
                                    minute, sekunda = parts
                                    if '.' not in sekunda:
                                        sekunda += '.000'
                                    return f"{date_str} {hour_str}:{minute}:{sekunda}"
                                elif len(parts) == 3:
                                    sat, minute, sekunda = parts
                                    if '.' not in sekunda:
                                        sekunda += '.000'
                                    return f"{date_str} {hour_str}:{minute}:{sekunda}"
                                else:
                                    return f"{date_str} {hour_str}:{t}"
                            else:
                                sekunda = t
                                if '.' not in sekunda:
                                    sekunda += '.000'
                                return f"{date_str} {hour_str}:00:{sekunda}"

                        chunk['time'] = chunk.apply(formiraj_time, axis=1)

                        def try_parsing_time(val):
                            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                                try:
                                    return pd.to_datetime(val, format=fmt)
                                except Exception:
                                    continue
                            return pd.NaT

                        chunk['time'] = chunk['time'].apply(try_parsing_time)
                        chunk = chunk.dropna(subset=['time'])
                        if chunk.empty:
                            continue

                        log.info(f"[{file}] Chunk {i+1}: {len(chunk)} redova za obradu ({timeframe})")
                        resampled = self.convert_to_timeframe(chunk, timeframe, index_col='time')
                        if resampled is None or resampled.empty:
                            continue
                        write_header = not os.path.exists(out_file) or os.path.getsize(out_file) == 0
                        resampled.reset_index().to_csv(out_file, mode='a', header=write_header, index=False)
                        log.info(f"Dodat chunk ({len(resampled)}) u {out_file} ({timeframe})")
                except Exception as e:
                    log.warning(f"⚠️ Ne mogu učitati {file_path}: {e}")

    def main_loop(self):
        while True:
            existing_files = self._get_existing_files()
            expected_files = set(self._expected_filenames())
            missing_files = list(expected_files - existing_files)
            missing_files.sort()
            if missing_files:
                log.info(f"Fali {len(missing_files)} fajlova. Skidam najnovije...")
                self._download_missing_files(missing_files)
                self.convert_and_append_new(missing_files)
            else:
                log.info("Svi fajlovi postoje, nema novih podataka.")
            for s in range(15 * 60, 0, -1):
                print(f"⏳ Sledeća provera za {s // 60:02d}:{s % 60:02d} min", end='\r')
                time.sleep(1)

if __name__ == "__main__":
    converter = DataConverter()
    converter.main_loop()
