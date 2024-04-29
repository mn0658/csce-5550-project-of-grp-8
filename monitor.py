import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    LOG_FILE = "file_changes.log"

    def __init__(self):
        super().__init__()
        self.log_file = open(self.LOG_FILE, "a")  # Open log file in append mode

    def __del__(self):
        self.log_file.close()  # Close log file when Handler instance is deleted

    def on_any_event(self, event):
        if event.is_directory:
            return None

        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event.event_type}: {event.src_path}\n"
        self.log_file.write(log_entry)
        self.log_file.flush()  # Flush buffer to ensure immediate writing to file

class Watcher:
    DIRECTORY_TO_WATCH = r"C:\Users\ruthi\OneDrive\Desktop\Critical_1"

    def __init__(self):
        self.observer = Observer()
        self.event_handler = Handler()  # Instantiate the Handler

    def run(self):
        self.observer.schedule(self.event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Observer Stopped")
            self.observer.join()  # Join observer thread upon stopping

if __name__ == "__main__":
    w = Watcher()
    w.run()