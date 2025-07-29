import os

# Struktura foldera
folders = ["logs", "reports/daily", "reports/weekly", "reports/monthly", "reports/yearly"]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("Struktura foldera je uspešno napravljena.")
