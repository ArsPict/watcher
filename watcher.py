import time
import psutil
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

#Constants
path = r'C:\MDS\WorkflowDefs'
app_name = "multidotscan"


class MyHandler(FileSystemEventHandler):
    def __init__(self, timeout, reaction):
        self.timeout = timeout
        self.reaction = reaction
        self.last_modified = time.time()
        self.at_work = False

    def on_any_event(self, event):
        self.last_modified = time.time()
        self.at_work = True

    def on_modified(self, event: FileSystemEvent) -> None:
        print(f"{time.time()}: Modified {event.src_path}")

    def on_created(self, event: FileSystemEvent) -> None:
        print(f"{time.time()}: Created {event.src_path}")

    def on_deleted(self, event: FileSystemEvent) -> None:
        print(f"{time.time()}: Deleted {event.src_path}")

    def on_moved(self, event: FileSystemEvent) -> None:
        print(f"{time.time()}: Moved {event.src_path}")

    def check_inactivity(self):
        if time.time() - self.last_modified > self.timeout and self.at_work:
            self.reaction()
            self.at_work = False


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
    root.attributes('-topmost', True)  # make sure the alert is on top
    message = f"The scanner has been inactive for the last {inactivity_duration // 60} minutes."
    messagebox.showinfo("Folder Inactivity Alert", message, parent=root)
    root.destroy()


if __name__ == "__main__":
    inactivity_duration = 240
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
