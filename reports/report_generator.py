import os
import pandas as pd
from datetime import datetime
from logs.logger import log
from utils.db_manager import get_trades_in_period, get_statistics_by_symbol, generate_daily_report

REPORT_DIR = os.path.join("reports")

def ensure_report_dir():
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
    except Exception as e:
        log.error(f"❌ Ne mogu da kreiram folder za izveštaje: {e}")

def export_report_to_excel(data, filename):
    """Snimi prosleđeni DataFrame kao .xlsx fajl."""
    try:
        filepath = os.path.join(REPORT_DIR, filename)
        data.to_excel(filepath, index=False)
        log.info(f"✅ Excel izveštaj snimljen: {filepath}")
        return filepath
    except Exception as e:
        log.error(f"❌ Greška pri snimanju Excel izveštaja: {e}")
        return None

def generate_period_report(start_date, end_date, symbol=None, filename=None):
    """Generiši Excel izveštaj za zadati period i simbol."""
    ensure_report_dir()
    trades = get_trades_in_period(start_date, end_date, symbol)
    if not trades:
        log.warning(f"⚠️ Nema trejdova za izveštaj {start_date} - {end_date}")
        return None
    columns = [
        "id", "symbol", "entry_time", "exit_time", "position_type", "entry_price",
        "exit_price", "stop_loss", "take_profit", "profit", "duration", "opened_by", "outcome"
    ]
    df = pd.DataFrame(trades, columns=columns)
    if not filename:
        symbol_part = f"_{symbol}" if symbol else ""
        filename = f"report_{start_date}_to_{end_date}{symbol_part}.xlsx"
    return export_report_to_excel(df, filename)

def generate_daily_reports(start_date, end_date):
    """Generiši dnevne Excel izveštaje za svaki dan u opsegu."""
    ensure_report_dir()
    date_list = pd.date_range(start=start_date, end=end_date)
    files = []
    for dt in date_list:
        date_str = dt.strftime("%Y-%m-%d")
        report = generate_daily_report(date_str)
        df = pd.DataFrame([report])
        filename = f"daily_report_{date_str}.xlsx"
        path = export_report_to_excel(df, filename)
        if path:
            files.append(path)
    return files

def generate_summary_report():
    """Generiši sumarni izveštaj po simbolima."""
    ensure_report_dir()
    stats = get_statistics_by_symbol()
    if not stats:
        log.warning("⚠️ Nema statistike za sumarni izveštaj.")
        return None
    df = pd.DataFrame(stats)
    filename = "summary_report.xlsx"
    return export_report_to_excel(df, filename)
