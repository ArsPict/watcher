import time
import psutil
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self, timeout, reaction):
        self.timeout = timeout
        self.reaction = reaction
        self.last_modified = time.time()

    def on_any_event(self, event):
        self.last_modified = time.time()

    def check_inactivity(self):
        if time.time() - self.last_modified > self.timeout:
            self.reaction()
            self.last_modified = time.time()  # reset to avoid continuous triggering


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


def show_inactivity_alert(inactivity_duration):
    root = tk.Tk()
    root.withdraw()  # hide the main window
    message = f"The folder has been inactive for the last {inactivity_duration // 60} minutes."
    messagebox.showinfo("Folder Inactivity Alert", message)
    root.destroy()


if __name__ == "__main__":
    path = r'C:\users\arsenii\pycharmprojects\watcher'
    app_name = "firefox"
    inactivity_duration = 10
    observer = Observer()
    event_handler = MyHandler(timeout=inactivity_duration, reaction=lambda: show_inactivity_alert(inactivity_duration))

    observer_started = False

    try:
        while True:
            if is_app_running(app_name):
                if not observer_started:
                    observer = Observer()
                    observer.schedule(event_handler, path, recursive=True)
                    observer.start()
                    observer_started = True
                    print(f"Started monitoring {path} because {app_name} is running.")
            else:
                if observer_started:
                    observer.stop()
                    observer.join()
                    observer_started = False
                    print(f"Stopped monitoring {path} because {app_name} is not running.")

            if observer_started:
                event_handler.check_inactivity()

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        if observer_started:
            observer.stop()
            observer.join()
        print("Observer has been shut down")
