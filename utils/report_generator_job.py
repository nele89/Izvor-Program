import os
import pandas as pd
from datetime import datetime, timedelta
from logs.logger import log
from utils.db_manager import get_trades_in_period

REPORT_DIRS = {
    "daily": "reports/daily_reports",
    "weekly": "reports/weekly_reports",
    "monthly": "reports/monthly_reports",
    "yearly": "reports/yearly_reports",
}

def ensure_dirs():
    for d in REPORT_DIRS.values():
        os.makedirs(d, exist_ok=True)

def get_period_dates(period):
    today = datetime.now().date()
    if period == "daily":
        start = today
        end = today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == "monthly":
        start = today.replace(day=1)
        end = today
    elif period == "yearly":
        start = today.replace(month=1, day=1)
        end = today
    else:
        raise Exception(f"Unknown period: {period}")
    return start, end

def report_generator_job(symbol="XAUUSD"):
    ensure_dirs()
    for period, folder in REPORT_DIRS.items():
        start_date, end_date = get_period_dates(period)
        df = get_trades_in_period(str(start_date), str(end_date), symbol=symbol)
        if df is None or df.empty:
            log.info(f"[REPORT] Nema trejdova za {symbol} ({period}) {start_date} - {end_date}")
            continue

        # Sve kolone koje postoje (prilagodljivo)
        out_cols = [
            "symbol", "entry_time", "exit_time", "position_type", "entry_price",
            "exit_price", "stop_loss", "take_profit", "profit", "duration",
            "opened_by", "outcome", "is_simulation", "decision", "indicators"
        ]
        export_cols = [col for col in out_cols if col in df.columns]
        df = df[export_cols]

        fname = f"{symbol}_{period}_report_{end_date}.csv"
        out_path = os.path.join(folder, fname)
        df.to_csv(out_path, index=False)

        # Excel verzija (bez greške ako nedostaje openpyxl)
        try:
            excel_path = out_path.replace(".csv", ".xlsx")
            df.to_excel(excel_path, index=False)
        except Exception as e:
            log.warning(f"[REPORT] Greška pri exportu u Excel: {e}")

        log.info(f"[REPORT] Generisan {period} izveštaj: {out_path}")

if __name__ == "__main__":
    report_generator_job()
