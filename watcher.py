import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime
import requests
import signal
import sys
import logging
from win10toast import ToastNotifier
import subprocess
from config_setup import setup_config
notifier = ToastNotifier()

# Configure logging
logging.basicConfig(
    filename=r".\logs\watcher_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


try:
    paths, app_settings, pushover_credentials = setup_config()
    path = paths['path']
    message_file = paths['message_file']
    inactivity_duration = app_settings['inactivity_duration']
    app_name = app_settings['app_name']
    USER_KEY = pushover_credentials['USER_KEY']
    APP_TOKEN = pushover_credentials['APP_TOKEN']
    # Access the constants
    print("Paths:", paths)
    print("App Settings:", app_settings)
    #print("Pushover Credentials:", pushover_credentials)

except Exception as e:
    print(f"Error: {str(e)}")


def send_pushover_notification(message):
    message = "test notification, please ignore \n" + message  # temporary
    print(f"message sent kwasi: {message}")  # temporary
    url = "https://api.pushover.net/1/messages.json"
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


def write_message_file(message):
    with open(message_file, "w") as file:
        file.write(message)


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
    write_message_file(message)
    try:
        # Trigger the Windows Task Scheduler to run the task
        subprocess.run(['schtasks', '/run', '/tn', 'pop_up_for_watcher'], check=True)
        logging.info("Inactivity notification triggered at %s", time.ctime())
    except subprocess.CalledProcessError as e:
        logging.error("Error triggering Task Scheduler: %s", str(e))


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
