import os
import shutil
from pathlib import Path
import traceback

# Konfiguracija
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKUP_DIR = PROJECT_ROOT / "backup_before_cleanup"
LOG_FILE = PROJECT_ROOT / "cleanup_log.txt"

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

def setup_logging():
    """Inicijalizacija log fajla"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("Cleanup Log\n===========\n")

def log_message(message):
    """Loguje poruku u fajl i na konzolu"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def backup_project():
    """Kreira backup pre modifikacija"""
    try:
        if BACKUP_DIR.exists():
            shutil.rmtree(BACKUP_DIR)
        shutil.copytree(PROJECT_ROOT, BACKUP_DIR, 
                       ignore=shutil.ignore_patterns('backup*', '.git'))
        log_message(f"✓ Backup kreiran u {BACKUP_DIR}")
    except Exception as e:
        log_message(f"❌ Greška pri backup-u: {str(e)}")
        raise

def safe_remove(path):
    """Bezbedno briše fajl ili folder"""
    try:
        if path.is_file():
            path.unlink()
            return True
        elif path.is_dir():
            shutil.rmtree(path)
            return True
    except Exception as e:
        log_message(f"⚠️ Neuspešno brisanje {path}: {str(e)}")
    return False

def remove_files():
    """Trajno briše fajlove/foldere"""
    removed = []
    failed = []
    
    for pattern in FILES_TO_REMOVE:
        try:
            for path in PROJECT_ROOT.rglob(pattern):
                if safe_remove(path):
                    removed.append(str(path))
        except Exception as e:
            failed.append(f"{pattern}: {str(e)}")
    
    if removed:
        log_message("🚮 Uklonjeno:")
        log_message("\n".join(f" - {f}" for f in removed))
    else:
        log_message("ℹ Nema fajlova za uklanjanje")
        
    if failed:
        log_message("\n❌ Greške pri uklanjanju:")
        log_message("\n".join(failed))

def safe_read_file(path):
    """Čita fajl sa automatskim otkrivanjem kodiranja"""
    encodings = ['utf-8', 'cp1252', 'iso-8859-1']
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Cannot decode {path} with tried encodings")

def fix_security():
    """Popravlja sigurnosne propuste"""
    # 1. Saniraj pickle.load()
    pickle_fixes = 0
    for py_file in PROJECT_ROOT.rglob("*.py"):
        try:
            content = safe_read_file(py_file)
            if "pickle.load(" in content:
                fixed = content.replace(
                    "pickle.load(",
                    "# WARNING: Replaced unsafe pickle.load()\n    # pickle.load("
                )
                py_file.write_text(fixed, encoding='utf-8')
                pickle_fixes += 1
                log_message(f"✓ Saniran pickle.load() u {py_file}")
        except Exception as e:
            log_message(f"⚠️ Greška pri obradi {py_file}: {str(e)}")
    
    # 2. Dodaj .gitignore
    try:
        gitignore = PROJECT_ROOT / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("\n".join(GITIGNORE_ENTRIES), encoding='utf-8')
            log_message("✓ Kreiran .gitignore")
    except Exception as e:
        log_message(f"❌ Greška pri kreiranju .gitignore: {str(e)}")

def main():
    setup_logging()
    log_message(f"🔍 Počinjem čišćenje projekta u {PROJECT_ROOT}")
    
    try:
        backup_project()
        remove_files()
        fix_security()
        log_message("✅ Čišćenje završeno! Proverite backup pre commit-a.")
    except Exception as e:
        log_message(f"❌ KATASTROFALNA GREŠKA: {str(e)}")
        log_message(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()