# reports/yearly_report.py
import os
import pandas as pd
from datetime import datetime
from utils.db_manager import get_statistics_by_symbol
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def export_yearly_report():
    stats = get_statistics_by_symbol()
    df = pd.DataFrame(stats)

    today = datetime.now().strftime("%Y-%m-%d")
    folder_excel = os.path.join("reports", "godišnji izveštaji")
    folder_pdf = os.path.join("reports", "godišnji izveštaji")
    os.makedirs(folder_excel, exist_ok=True)
    os.makedirs(folder_pdf, exist_ok=True)

    path_excel = os.path.join(folder_excel, f"{today}_yearly.xlsx")
    path_pdf = os.path.join(folder_pdf, f"{today}_yearly.pdf")

    df.to_excel(path_excel, index=False)
    print(f"✅ Godišnji izveštaj snimljen: {path_excel}")

    # --- PDF ---
    c = canvas.Canvas(path_pdf, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, f"Godišnji izveštaj ({today})")

    y = 770
    for _, row in df.iterrows():
        c.setFont("Helvetica", 10)
        text = f"{row.get('symbol', '')}: profit={row.get('total_profit', '')}, avg={row.get('avg_profit', '')}, total={row.get('total_trades', '')}"
        c.drawString(50, y, text)
        y -= 20
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    print(f"✅ Godišnji PDF izveštaj snimljen: {path_pdf}")