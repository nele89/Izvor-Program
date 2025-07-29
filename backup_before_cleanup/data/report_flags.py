import os
import json
from datetime import datetime

FLAGS_FILE = "data/flags/report_flags.json"

def load_report_flags():
    if not os.path.exists(FLAGS_FILE):
        return {"daily": [], "weekly": [], "monthly": [], "yearly": []}
    with open(FLAGS_FILE, "r") as f:
        return json.load(f)

def save_report_flags(flags):
    os.makedirs(os.path.dirname(FLAGS_FILE), exist_ok=True)
    with open(FLAGS_FILE, "w") as f:
        json.dump(flags, f, indent=2)

def report_already_generated(period_type, date_str):
    flags = load_report_flags()
    return date_str in flags.get(period_type, [])

def mark_report_generated(period_type, date_str):
    flags = load_report_flags()
    if period_type not in flags:
        flags[period_type] = []
    if date_str not in flags[period_type]:
        flags[period_type].append(date_str)
    save_report_flags(flags)
