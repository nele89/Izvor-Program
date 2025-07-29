import os
import shutil
from logs.logger import log

def ensure_dir_exists(path):
    """Kreira folder ako ne postoji."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        log.error(f"❌ Ne mogu da kreiram direktorijum {path}: {e}")
        return False

def move_file(src, dst):
    """Premesti fajl sa src na dst."""
    try:
        ensure_dir_exists(os.path.dirname(dst))
        shutil.move(src, dst)
        log.info(f"✅ Premesten fajl: {src} → {dst}")
        return True
    except Exception as e:
        log.error(f"❌ Ne mogu da premestim fajl {src} → {dst}: {e}")
        return False

def copy_file(src, dst):
    """Kopira fajl sa src na dst."""
    try:
        ensure_dir_exists(os.path.dirname(dst))
        shutil.copy2(src, dst)
        log.info(f"✅ Kopiran fajl: {src} → {dst}")
        return True
    except Exception as e:
        log.error(f"❌ Ne mogu da kopiram fajl {src} → {dst}: {e}")
        return False

def remove_file(path):
    """Briše fajl na datoj putanji."""
    try:
        if os.path.isfile(path):
            os.remove(path)
            log.info(f"🗑️ Obrišan fajl: {path}")
            return True
        else:
            log.warning(f"⚠️ Fajl ne postoji: {path}")
            return False
    except Exception as e:
        log.error(f"❌ Greška pri brisanju fajla {path}: {e}")
        return False

def list_files(folder, extension=None):
    """Vrati listu fajlova iz foldera (može i po ekstenziji)."""
    try:
        files = []
        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                if extension is None or filename.endswith(extension):
                    files.append(os.path.join(root, filename))
        return files
    except Exception as e:
        log.error(f"❌ Greška pri listanju fajlova u {folder}: {e}")
        return []

def archive_file(src, archive_dir):
    """Arhivira fajl tako što ga prebacuje u archive_dir."""
    try:
        ensure_dir_exists(archive_dir)
        dst = os.path.join(archive_dir, os.path.basename(src))
        shutil.move(src, dst)
        log.info(f"📦 Arhiviran fajl: {src} → {dst}")
        return True
    except Exception as e:
        log.error(f"❌ Ne mogu da arhiviram fajl {src}: {e}")
        return False
