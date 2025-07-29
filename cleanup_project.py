import os
import shutil
from pathlib import Path

# Konfiguracija
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKUP_DIR = PROJECT_ROOT / "backup_before_cleanup"
FILES_TO_REMOVE = [
    # Sigurnosni rizici
    ".env", "config.ini", "config_backup.ini", 
    "mt5_connector.py", "autosave_git.py",
    
    # Duplikati
    "ai/ai_engine.py", "engine/ai_engine.py",
    "ai/feature_extractor.py", "utils/feature_extractor.py",
    
    # Privremeni/log fajlovi
    "logs/archive/", "*.log", "*.tmp", "temp_*.csv",
    
    # Debug/star fajlovi
    "show_errors.py", "old/", "__pycache__/"
]
GITIGNORE_ENTRIES = [
    "# Sigurnosno",
    ".env", "*.ini", "*.pkl",
    "# Logovi/privremeno",
    "*.log", "*.tmp", "temp_*",
    "# Python cache",
    "__pycache__/", "*.py[cod]"
]

def backup_project():
    """Kreira backup pre modifikacija"""
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(PROJECT_ROOT, BACKUP_DIR, 
                   ignore=shutil.ignore_patterns('backup*', '.git'))
    print(f"✓ Backup kreiran u {BACKUP_DIR}")

def remove_files():
    """Trajno briše fajlove/foldere"""
    removed = []
    for pattern in FILES_TO_REMOVE:
        for path in PROJECT_ROOT.rglob(pattern):
            if path.is_file():
                path.unlink()
                removed.append(str(path))
            elif path.is_dir():
                shutil.rmtree(path)
                removed.append(f"{str(path)}/")
    
    if removed:
        print("🚮 Uklonjeno:")
        print("\n".join(f" - {f}" for f in removed))
    else:
        print("ℹ Nema fajlova za uklanjanje")

def fix_security():
    """Popravlja sigurnosne propuste"""
    # 1. Saniraj pickle.load()
    for py_file in PROJECT_ROOT.rglob("*.py"):
        content = py_file.read_text()
        if "pickle.load(" in content:
            fixed = content.replace(
                "pickle.load(",
                "# WARNING: Replaced unsafe pickle.load()\n    # pickle.load("
            )
            py_file.write_text(fixed)
            print(f"✓ Saniran pickle.load() u {py_file}")
    
    # 2. Dodaj .gitignore
    gitignore = PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("\n".join(GITIGNORE_ENTRIES))
        print("✓ Kreiran .gitignore")

def main():
    print(f"🔍 Počinjem čišćenje projekta u {PROJECT_ROOT}")
    backup_project()
    remove_files()
    fix_security()
    print("✅ Čišćenje završeno! Proverite backup pre commit-a.")

if __name__ == "__main__":
    main()