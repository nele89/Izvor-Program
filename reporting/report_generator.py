import os
import pandas as pd
from datetime import datetime
from logs.logger import log
from reporting.report_utils import calculate_basic_statistics, filter_by_period

BASE_REPORT_FOLDER = "reports"
PARQUET_PATH = "data/dukascopy/parquet_resampled/XAUUSD_M1.parquet"  # Prilagodi putanju!

def load_trades():
    try:
        if not os.path.exists(PARQUET_PATH):
            log.error(f"❌ Parquet fajl ne postoji: {PARQUET_PATH}")
            return pd.DataFrame()
        df = pd.read_parquet(PARQUET_PATH)
        if "time" in df.columns:
            df.rename(columns={"time": "entry_time"}, inplace=True)
        return df
    except Exception as e:
        log.error(f"❌ Greška pri učitavanju trejdova iz Parquet-a: {e}")
        return pd.DataFrame()

def make_report(period="daily", output_format="excel"):
    df_all = load_trades()
    df = filter_by_period(df_all, period)

    if df.empty:
        log.warning(f"📝 Nema podataka za {period} izveštaj.")
        return False

    stats = calculate_basic_statistics(df)
    now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder = os.path.join(BASE_REPORT_FOLDER, period)
    os.makedirs(folder, exist_ok=True)
    filename = f"{period}_report_{now}"

    if output_format in ["excel", "both"]:
        path = os.path.join(folder, filename + ".xlsx")
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, sheet_name="Trades", index=False)
            pd.DataFrame([stats]).to_excel(writer, sheet_name="Summary", index=False)
        log.info(f"✅ Excel izveštaj sačuvan: {path}")

    if output_format in ["pdf", "both"]:
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages

            pdf_path = os.path.join(folder, filename + ".pdf")
            with PdfPages(pdf_path) as pdf:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis("off")
                tbl = ax.table(cellText=df.head(20).values,
                               colLabels=df.columns,
                               loc="center")
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close()
            log.info(f"✅ PDF izveštaj sačuvan: {pdf_path}")
        except Exception as e:
            log.error(f"❌ PDF generisanje nije uspelo: {e}")

    return True

if __name__ == "__main__":
    for period in ["daily", "weekly", "monthly", "yearly"]:
        make_report(period, output_format="both")
