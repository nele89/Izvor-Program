import os

FOLDERS = [
    "logs",
    "logs/archive",
    "data",
    "data/dukascopy",
    "data/histdata",
    "data/converted_data",
    "db",
    "config",
    "reports",
    "reports/daily_reports",
    "reports/weekly_reports",
    "reports/monthly_reports",
    "reports/yearly_reports",
    "reports/pdf_reports",
    "ui",
    "ui/components",
    "ai",
    "ai/models",
    "strategy",
    "backend",
    "utils",
    "data/downloader"
]

def create_folders():
    for folder in FOLDERS:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Kreiran folder: {folder}")
        except Exception as e:
            print(f"❌ Greška pri kreiranju {folder}: {e}")

if __name__ == "__main__":
    create_folders()
