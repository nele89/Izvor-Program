# reporting/report_launcher.py

from reporting.report_generator import make_report

def generate_all_reports(output_format="both"):
    for period in ["daily", "weekly", "monthly", "yearly"]:
        print(f"📊 Generišem izveštaj za: {period}")
        make_report(period=period, output_format=output_format)

def generate_single_report(period="daily", output_format="excel"):
    print(f"📄 Generišem samo jedan izveštaj: {period}")
    make_report(period=period, output_format=output_format)

if __name__ == "__main__":
    generate_all_reports(output_format="both")
