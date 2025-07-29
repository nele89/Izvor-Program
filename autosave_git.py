#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_ROOT = os.getcwd()

# --- Pomoćne funkcije za Git ---
def run(*args):
    return subprocess.run(args, cwd=PROJECT_ROOT)

def run_out(*args):
    return subprocess.run(args, cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.strip()

def ensure_git_setup():
    # .git folder
    if not os.path.isdir(os.path.join(PROJECT_ROOT, '.git')):
        print("ERROR: .git folder nije pronađen.")
        sys.exit(1)
    print("✔ .git folder pronađen")

    # remote origin
    remotes = run_out('git', 'remote').split()
    if 'origin' not in remotes:
        print("ERROR: remote 'origin' nije postavljen.")
        sys.exit(1)
    print("✔ remote 'origin' konfigurisan")

    # grana main
    branch = run_out('git', 'rev-parse', '--abbrev-ref', 'HEAD')
    if branch != 'main':
        print(f"⚠ Prebacujem granu '{branch}' na 'main'")
        run('git', 'branch', '-M', 'main')
    else:
        print("✔ Aktuelna grana je 'main'")

    # tracking
    track = run_out('git', 'config', 'branch.main.remote')
    if track != 'origin':
        print(f"⚠ Podesiću da 'main' prati 'origin'")
        run('git', 'branch', '--set-upstream-to', 'origin/main', 'main')
    else:
        print("✔ Grana 'main' prati 'origin'")

def ensure_vscode_settings():
    cfg_dir = os.path.join(PROJECT_ROOT, '.vscode')
    os.makedirs(cfg_dir, exist_ok=True)
    settings_path = os.path.join(cfg_dir, 'settings.json')
    settings = {
        "autogitcommit.enable": True,
        "autogitcommit.push": True,
        "autogitcommit.commitMessage": "Auto-save: ${fileBasename}",
        "autogitcommit.branch": "main"
    }
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)
    print(f"✔ Ažuriran VS Code settings u {settings_path}")

class GitAutoHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._last = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        path = event.src_path
        rel = os.path.relpath(path, PROJECT_ROOT)
        # izuzmi .git i .vscode foldere
        if rel.startswith('.git') or rel.startswith('.vscode'):
            return
        now = time.time()
        # debouncing
        if rel in self._last and now - self._last[rel] < 1:
            return
        self._last[rel] = now

        # kratko se sačekaj da se fajl zatvori
        time.sleep(0.2)
        print(f"⏳ Detektovana izmena: {rel}")
        # Git add/commit/push
        run('git', 'add', '-A')
        diff = subprocess.run(['git','diff-index','--quiet','HEAD','--'], cwd=PROJECT_ROOT).returncode
        if diff != 0:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            msg = f"Auto-save: {rel} at {ts}"
            run('git', 'commit', '-m', msg)
            run('git', 'push')
            print(f"✔ {msg}")

def main():
    print("🔧 Proveravam Git i VS Code podešavanja…")
    ensure_git_setup()
    ensure_vscode_settings()

    print("\n📡 Pokrećem watcher (pritisnite Ctrl+C za prekid)…")
    event_handler = GitAutoHandler()
    observer = Observer()
    observer.schedule(event_handler, path=PROJECT_ROOT, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("🛑 Watcher zaustavljen.")

if __name__ == '__main__':
    main()
