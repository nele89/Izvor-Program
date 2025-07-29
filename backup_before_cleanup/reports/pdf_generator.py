from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime
from logs.logger import log
from utils.db_manager import get_statistics_by_symbol, get_all_trades

PDF_DIR = "reports/pdf_reports"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def generate_pdf_report(report_type="daily", date_str=None):
    """
    Generiše PDF izveštaj o trgovanju (daily/weekly/monthly/yearly).
    """
    ensure_dir(PDF_DIR)
    today = datetime.now().strftime("%Y-%m-%d")
    if date_str is None:
        date_str = today

    filename = f"{report_type}_report_{date_str}.pdf"
    out_path = os.path.join(PDF_DIR, filename)
    log.info(f"📝 Kreiram PDF izveštaj: {out_path}")

    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Naslov
    story.append(Paragraph(f"{report_type.capitalize()} Trading Report - {date_str}", styles["Title"]))
    story.append(Spacer(1, 12))

    # Kratka statistika po simbolima
    stats = get_statistics_by_symbol()
    table_data = [["Symbol", "Trades", "Total Profit", "Avg Profit", "Max Profit", "Min Profit"]]
    for s in stats:
        table_data.append([
            s["symbol"],
            s["total_trades"],
            f"{s['total_profit']:.2f}",
            f"{s['avg_profit']:.2f}",
            f"{s['max_profit']:.2f}",
            f"{s['min_profit']:.2f}"
        ])

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    story.append(table)
    story.append(Spacer(1, 18))

    # Po želji: Detalji svih trejdova (prvih 15 radi primere)
    trades = get_all_trades()
    if trades:
        trade_table_data = [["Symbol", "Open Time", "Close Time", "Type", "Volume", "Profit"]]
        for t in trades[:15]:
            trade_table_data.append([
                t[1], t[2], t[3], t[4], t[5], f"{t[9]:.2f}"
            ])
        trade_table = Table(trade_table_data, hAlign="LEFT")
        trade_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightskyblue),
            ("TEXTCOLOR", (0,0), (-1,0), colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("BOTTOMPADDING", (0,0), (-1,0), 4),
            ("GRID", (0,0), (-1,-1), 0.3, colors.grey)
        ]))
        story.append(Paragraph("Detalji trejdova (prvih 15):", styles["Heading3"]))
        story.append(trade_table)

    # Sačuvaj PDF
    try:
        doc.build(story)
        log.info(f"✅ PDF izveštaj sačuvan: {out_path}")
    except Exception as e:
        log.error(f"❌ Greška pri snimanju PDF izveštaja: {e}")

if __name__ == "__main__":
    generate_pdf_report(report_type="daily")
