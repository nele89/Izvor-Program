# 📁 reports/exporter.py

from reports.daily_report import export_daily_report
from reports.weekly_report import export_weekly_report
from reports.monthly_report import export_monthly_report
from reports.yearly_report import export_yearly_report

def export_all_reports():
    export_daily_report()
    export_weekly_report()
    export_monthly_report()
    export_yearly_report()
