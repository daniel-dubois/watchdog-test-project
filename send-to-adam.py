# Author: Daniel DuBois
# Date: 2-27-2024
# Description: Daemon that monitors a directory for new directories, then waits for a ".jpg" file and
# a ".json" file to appear in the subdirectory. The paths to the two files are stored variables, then 
# passed into a post() function that sends them to Adam's app server.

import os
import time
import subprocess
import requests
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

url = 'https://verified-duly-katydid.ngrok-free.app'

class eventsHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print("New directory detected")
            path_to_jpg = wait_for_jpg(event.src_path, timeout=30) # wait for 30s, return jpg if it appears, otherwise print error msg
            path_to_json = wait_for_json(event.src_path, timeout=1) # wait a small amount of time for json to appear (ask Andrew to make json no matter what?)
            
            post(path_to_jpg, path_to_json) # send jpg and json to server

            # for testing:
            print("Detected .jpg file at ", path_to_jpg)
            if path_to_json is not None:
                print("Detected .json file at ", path_to_json)
            else:
                print("Did not detect .json file in directory ", event.src_path) 

def wait_for_jpg(directory, timeout=None):
    start_time = time.time()

    while True:
        for file_name in os.listdir(directory):
            if file_name.endswith(".jpg"):
                return os.path.join(directory, file_name)
        if timeout is not None and time.time() - start_time > timeout:
            print("Error: Timeout waiting for .jpg to appear in directory \" ", directory, "\".")
            return None
        time.sleep(0.1) # check every 0.1s for the .jpg file to appear (can be adjusted lower if needed)

def wait_for_json(directory, timeout=None):
    start_time = time.time()

    while True:
        for file_name in os.listdir(directory):
            if file_name.endswith(".json"):
                return os.path.join(directory, file_name)
        if timeout is not None and time.time() - start_time > timeout:
            # print("Error: Timeout waiting for .json to appear in directory \" ", directory, "\".") # UNCOMMENT if .json is changed to always generate (even when no labels are found in the photo)
            return None
        time.sleep(0.1) # check every 0.1s for the .json file to appear (can be adjusted lower if needed)

def post(path_to_jpg, path_to_json):
    json_obj = json.load(open(path_to_json,'rb'))

    package = {
        'Image': (os.path.basename(path_to_jpg), open(path_to_jpg, 'rb'), 'image/jpg'), # ask Adam if name should include ".jpg" extension or not
    }
    data = {
        'Category': (None, json_obj['Category'], 'text/plain'),
        'timeStamp': (None, json_obj['timeStamp'], 'text/plain') # ask Adam what timeStamp is used for, work w/ Andrew to generate it in the json
    }

    r = requests.post(url, files=package, data=data)

    print(r.text) #debugging, comment out for final use
    print(r.status_code) #debugging, comment out for final use (only prints one line so might just keep)

if __name__ == "__main__":
    path = "." # path to directory to monitor for new directories (where image processing makes new directories for each run)
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