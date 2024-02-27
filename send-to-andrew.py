# Author: Daniel DuBois
# Date: 2-27-2024
# Description: Daemon that monitors a directory for new files ending in ".jpg" and
# calls a subprocess (detect.py), passing in the new jpeg

import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class eventsHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".jpg"):
            subprocess.run("python", "detect.py", "--weights", "best.pt", "--source", event.src_path, "--no-trace") # call andrew
            # print("New .jpg detected")

if __name__ == "__main__":
    path = "." # path to directory to monitor for new .jpgs
    event_handler = eventsHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()