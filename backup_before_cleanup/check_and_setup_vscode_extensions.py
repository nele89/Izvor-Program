#!/usr/bin/env python3
"""
check_and_setup_vscode_extensions.py

Ovaj skript proverava i automatski podešava VS Code ekstenzije za
automatski Git commit/push pri čuvanju fajla, kao i .vscode/settings.json.

Kako radi:
1) Proverava dostupnost `code --version` preko shell=True.
2) Ako CLI radi, proverava i po potrebi instalira:
   - YogeshValiya.autogitcommit
   - emeraldwalk.runonsave
3) Kreira ili ažurira .vscode/settings.json sa neophodnim podešavanjima.
"""

import subprocess
import json
import os
import sys

errors = 0

def ok(msg):
    print(f"[OK]   {msg}")

def err(msg):
    global errors
    errors += 1
    print(f"[ERR]  {msg}")

def run_cmd(cmd):
    """Pokreće komandu u shell-u i vraća (rc, stdout, stderr)."""
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def check_code_cli():
    rc, out, err_out = run_cmd('code --version')
    if rc == 0:
        ok(f"VS Code CLI dostupan: {out.splitlines()[0]}")
    else:
        err("VS Code CLI (`code`) nije dostupan u PATH — proveri 'Shell Command: Install code in PATH' u VS Code-u.")
        sys.exit(1)

def ensure_extension(ext_id):
    rc, out, _ = run_cmd('code --list-extensions')
    installed = out.splitlines()
    if ext_id in installed:
        ok(f"Ekstenzija '{ext_id}' već instalirana")
    else:
        ok(f"Instaliram ekstenziju '{ext_id}'...")
        rc2, out2, err2 = run_cmd(f'code --install-extension {ext_id}')
        if rc2 == 0:
            ok(f"Ekstenzija '{ext_id}' uspešno instalirana")
        else:
            err(f"Neuspešna instalacija '{ext_id}': {err2}")

def ensure_settings():
    cfg_dir = os.path.join(os.getcwd(), '.vscode')
    os.makedirs(cfg_dir, exist_ok=True)
    path = os.path.join(cfg_dir, 'settings.json')
    settings = {
        "autogitcommit.enable": True,
        "autogitcommit.push": True,
        "autogitcommit.commitMessage": "Auto-save: ${fileBasename}",
        "autogitcommit.branch": "main",
        "emeraldwalk.runonsave": {
            "commands": [
                {
                    "match": ".*",
                    "command": "powershell -ExecutionPolicy Bypass -NoProfile -File \"${workspaceFolder}/auto_git_push.ps1\""
                }
            ]
        }
    }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        ok(f"Ažurirano {path}")
    except Exception as e:
        err(f"Neuspešno pisanje {path}: {e}")

def main():
    print("🔧 Provera i automatsko podešavanje VS Code ekstenzija i settings.json\n")
    check_code_cli()
    for ext in ('YogeshValiya.autogitcommit', 'emeraldwalk.runonsave'):
        ensure_extension(ext)
    ensure_settings()
    print(f"\n=== Rezime: pronađeno {errors} grešaka ===")
    sys.exit(errors)

if __name__ == '__main__':
    main()
