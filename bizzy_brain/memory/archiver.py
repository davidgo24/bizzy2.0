# bizzy-gemini-version-scaffold/bizzy_brain/memory/archiver.py

import os
import shutil
from datetime import datetime, timedelta
from ..config import CLIENT_THREADS_DIR, ARCHIVES_DIR

def archive_stale_threads(days_stale: int = 7):
    print(f"\n🧹 Archiving threads older than {days_stale} days...")
    os.makedirs(ARCHIVES_DIR, exist_ok=True)
    cutoff_date = datetime.now() - timedelta(days=days_stale)

    for filename in os.listdir(CLIENT_THREADS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(CLIENT_THREADS_DIR, filename)
            # Get modification time of the file
            mod_timestamp = os.path.getmtime(file_path)
            mod_date = datetime.fromtimestamp(mod_timestamp)

            if mod_date < cutoff_date:
                archive_path = os.path.join(ARCHIVES_DIR, filename)
                shutil.move(file_path, archive_path)
                print(f"Archived: {filename}")
    print("Archiving complete.")
