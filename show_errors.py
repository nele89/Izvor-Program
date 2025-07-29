import os
import re

LOGS_DIR = "logs"

# Pronađi sve log fajlove (možeš dodati filter za .log fajlove)
log_files = [f for f in os.listdir(LOGS_DIR) if f.endswith(".log")]

# Ključne reči za probleme
problem_keywords = [
    "error", "greška", "fail", "exception", "warning", "critical",
    "nije moguće", "problem", "neuspešno", "not found", "abort", "traceback"
]

regex_pattern = re.compile(r"(" + "|".join(problem_keywords) + ")", re.IGNORECASE)

found = False
for log_file in log_files:
    path = os.path.join(LOGS_DIR, log_file)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for line in lines:
            if regex_pattern.search(line):
                print(f"{log_file}: {line.strip()}")
                found = True

if not found:
    print("✅ Nije pronađena nijedna greška ili problem u log fajlovima.")
