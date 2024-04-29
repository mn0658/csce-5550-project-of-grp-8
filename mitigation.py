import os
import time
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict, deque
import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ACCOUNT = ''
EMAIL_PASSWORD = ''  
class Detection(FileSystemEventHandler):
    def __init__(self, backup_directory):
        self.folder_access_log = defaultdict(lambda: deque(maxlen=100))
        self.backup_directory = backup_directory

    def on_modified(self, event):
        if not event.is_directory:
            self.log(event.src_path, 'modified')

    def on_created(self, event):
        if not event.is_directory:
            self.log(event.src_path, 'created')

    def log(self, path, event_type):
        folder_path = '/'.join(path.split('\\'))  # Adjust path splitting for consistency
        event_timestamp = pd.Timestamp.now()
        new_event = {'timestamp': event_timestamp, 'file_path': path, 'event_type': event_type}
        self.folder_access_log[folder_path].append(new_event)
        self.anomaly_detection(folder_path)

    def anomaly_detection(self, folder_path):
        current_time = pd.Timestamp.now()
        recent_events = [event for event in self.folder_access_log[folder_path] if event['timestamp'] > current_time - pd.Timedelta(seconds=10)]
        if len(recent_events) > 5:
            print(f"Threat detected in {folder_path}: high frequency of file operations detected.")
            subject = "Suspicious Activity Detected"
            body = f"High frequency of file operations detected in {folder_path}. Immediate action will be taken."
            self.send_email(subject, body, 'admin@example.com')  # Send email first
            self.log_for_investigation(folder_path, recent_events)
            self.mitigate(folder_path)

    def send_email(self, subject, body, recipient):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, recipient, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {str(e)}")

    def mitigate(self, folder_path):
        self.lock_directory(folder_path)
        self.restore_files(self.backup_directory, folder_path)

    def lock_directory(self, path):
        os.system(f"icacls '{path}' /deny everyone:(OI)(CI)F")
        print(f"Access to {path} has been locked.")

    def restore_files(self, backup_dir, target_dir):
        for file_name in os.listdir(backup_dir):
            source_file = os.path.join(backup_dir, file_name)
            target_file = os.path.join(target_dir, file_name)
            shutil.copy(source_file, target_file)
        print(f"Files have been restored from backup to {target_dir}")

# Path setup and observer initialization
backup_directory = r""
path_to_monitor = r""
event_handler = Detection(backup_directory)
observer = Observer()
observer.schedule(event_handler, path_to_monitor, recursive=True)

observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
