import time
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict, deque
import datetime

class Detection(FileSystemEventHandler):
    def __init__(self):
        # Using defaultdict to automatically handle any folder not previously accessed
        self.folder_access_log = defaultdict(lambda: deque(maxlen=100))

    def on_modified(self, event):
        if not event.is_directory:
            self.log(event.src_path, 'modified')

    def on_created(self, event):
        if not event.is_directory:
            self.log(event.src_path, 'created')

    def log(self, path, event_type):
        # Extract folder path from file path
        folder_path = '/'.join(path.split('/')[:-1])
        event_timestamp = pd.Timestamp.now()
        
        # Log file access event with the current timestamp
        new_event = {'timestamp': event_timestamp, 'file_path': path, 'event_type': event_type}
        self.folder_access_log[folder_path].append(new_event)
        
        # Check for anomaly after logging the event
        self.anomaly(folder_path)

    def anomaly(self, folder_path):
        # Analyze recent events within the last 10 seconds for the specified folder
        current_time = pd.Timestamp.now()
        recent_events = [event for event in self.folder_access_log[folder_path] if event['timestamp'] > current_time - pd.Timedelta(seconds=10)]

        # Detect high frequency of file operations
        if len(recent_events) > 5:
            print(f"Threat detected in {folder_path}: high frequency of file operations detected.")
            self.log_for_investigation(folder_path, recent_events)

    def log_for_investigation(self, folder_path, events):
        # Log details to a file or a monitoring system for further investigation
        with open("suspicious_activity_log.txt", "a") as file:
            file.write(f"Unusual activity detected on {datetime.datetime.now()} for folder {folder_path}:\n")
            for event in events:
                file.write(f"{event['timestamp']} - {event['event_type']} - {event['file_path']}\n")
            file.write("\n")

path_to_monitor = "C:\\Users\\ruthi\\OneDrive\\Desktop\\Critical_1"  
event_handler = Detection()
observer = Observer()
observer.schedule(event_handler, path_to_monitor, recursive=True)

observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
