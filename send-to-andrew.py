

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
    # do stuff
    path = "." # try with different paths
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
    

