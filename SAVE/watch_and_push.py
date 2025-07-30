import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

WATCHED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUSH_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "auto_git_push.ps1"))

class SaveHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in [".py", ".json", ".txt", ".md"]):
            print(f"[📝 Detektovana izmena]: {event.src_path}")
            subprocess.call(["powershell", "-ExecutionPolicy", "Bypass", "-File", PUSH_SCRIPT])

if __name__ == "__main__":
    print(f"🔍 Posmatram: {WATCHED_DIR}")
    event_handler = SaveHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCHED_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
