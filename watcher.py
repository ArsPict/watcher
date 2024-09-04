import time
import psutil
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime
import requests
import signal
import sys
import logging
from win10toast import ToastNotifier
notifier = ToastNotifier()


# Configure logging
logging.basicConfig(
    filename=r".\logs\watcher_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


#Constants
#path = r'C:\MDS\WorkflowDefs'
#app_name = "multidotscan"

path = r'C:\Users\Arsenii\pascal_projects'
app_name = "pascalABC.NET"
inactivity_duration = 15

# token and key for the pushover service
USER_KEY = 'unm6h553h251f8upmssx5p5rbem881'
APP_TOKEN = 'ac4b78642pz97vcifowhe4bmorpz6w'

def send_pushover_notification(message):
    message = "test notification, please ignore \n" + message  # temporary
    print(f"message sent kwasi: {message}")                    # temporary
    '''url = "https://api.pushover.net/1/messages.json"
    data = {
        'token': APP_TOKEN,
        'user': USER_KEY,
        'message': message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification: {response.text}")
    '''


class MyHandler(FileSystemEventHandler):
    def __init__(self, timeout, reaction):
        self.timeout = timeout
        self.reaction = reaction
        self.last_modified = time.time()
        self.at_work = False
        self.hms_time = datetime.now().strftime("%H:%M:%S")

    def on_any_event(self, event):
        self.last_modified = time.time()
        self.at_work = True
        self.hms_time = datetime.now().strftime("%H:%M:%S")

    def on_modified(self, event: FileSystemEvent) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        m = f"{current_time}: Modified {event.src_path}"
        print(m)
        logging.info(m)

    def on_created(self, event: FileSystemEvent) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        m = f"{current_time}: Created {event.src_path}"
        print(m)
        logging.info(m)

    def on_deleted(self, event: FileSystemEvent) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        m = f"{current_time}: Deleted {event.src_path}"
        print(m)
        logging.info(m)

    def on_moved(self, event: FileSystemEvent) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        m = f"{current_time}: Moved {event.src_path}"
        print(m)
        logging.info(m)

    def check_inactivity(self):
        if time.time() - self.last_modified > self.timeout and self.at_work:
            self.reaction()
            self.at_work = False
            m = "the scanner is idle, notification sent"
            print(m)
            logging.info(m)
        else:
            if self.at_work:
                m = (f""
                     f"inactivity begin: {datetime.fromtimestamp(self.last_modified).strftime('%H:%M:%S')}, "
                     f"time till alert: {(self.timeout - time.time() + self.last_modified):.2f}")
            else:
                m = (f"inactivity begin: {datetime.fromtimestamp(self.last_modified).strftime('%H:%M:%S')}, "
                     f"not at work")
            print(m)
            logging.info(m)


def is_app_running(app_name):
    """Check if there is any running process that contains the given app_name."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline is None:
                cmdline = []
            if app_name.lower() in proc.info['name'].lower() or app_name.lower() in ' '.join(cmdline).lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def inactivity_alert(last_modified):
    send_pushover_notification(inactivity_message(last_modified))
    inactivity_pop_up(last_modified)


def inactivity_message(last_modified):
    inactivity_duration = time.time() - last_modified
    message = f"""
                    Der Scanner ist in den letzten {inactivity_duration // 60} Minuten inaktiv geblieben.
                    Inaktivitätsbegin: {datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}"""
    return message


def inactivity_pop_up(last_modified):
    inactivity_duration = time.time() - last_modified
    message = f"""
                    The scanner has been inactive for the last {inactivity_duration // 60} minutes.
                    Der Scanner ist in den letzten {inactivity_duration // 60} Minuten inaktiv geblieben."""
    try:
        notifier.show_toast("Scanner Inactivity Alert", message, duration=10)
    except Exception as e:
        logging.basicConfig(filename='error_log.log',
                            level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error("Error displaying toast notification", exc_info=True)
    finally:
        logging.basicConfig(
            filename=r".\logs\watcher_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s"
        )


"""
    def inactivity_pop_up(last_modified):
    inactivity_duration = time.time() - last_modified
    root = tk.Tk()
    root.withdraw()  # hide the main window
    root.attributes('-topmost', True)  # make sure the alert is on top
    message = (f""
               f"The scanner has been inactive for the last {inactivity_duration // 60} minutes.\n"
               f"Der Scanner ist in den letzten {inactivity_duration // 60} Minuten inaktiv geblieben.")
    messagebox.showinfo("Scanner Inactivity Alert", message, parent=root)
    root.destroy()
"""

def signal_handler(sig, frame):
    message = f"Script was stopped by signal {sig} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    send_pushover_notification(message)
    m = "Shutting down..."
    print(m)
    logging.info(m)
    sys.exit(0)


if __name__ == "__main__":
    m = "Service has started."
    logging.info(m)
    print(m)
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal

    observer = Observer()
    event_handler = MyHandler(timeout=inactivity_duration,
                              reaction=lambda: inactivity_alert(event_handler.last_modified))

    observer_started = False

    try:
        while True:
            if is_app_running(app_name):
                if not observer_started:
                    observer = Observer()
                    observer.schedule(event_handler, path, recursive=True)
                    observer.start()
                    observer_started = True
                    event_handler.last_modified = time.time()
                    logging.info(f"Started monitoring {path} because {app_name} is running.")
                    print(f"Started monitoring {path} because {app_name} is running.")
            else:
                if observer_started:
                    observer.stop()
                    observer.join()
                    observer_started = False
                    logging.info(f"Stopped monitoring {path} because {app_name} is not running.")
                    print(f"Stopped monitoring {path} because {app_name} is not running.")
            if observer_started:
                event_handler.check_inactivity()

            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    finally:
        if observer_started:
            observer.stop()
            observer.join()
        m = "Observer has been shut down"
        print(m)
        logging.info(m)
