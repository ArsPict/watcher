import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import psutil


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, timeout, reaction):
        self.timeout = timeout
        self.reaction = reaction
        self.last_modified = time.time()

    def on_any_event(self, event: FileSystemEvent):
        self.last_modified = time.time()

    def check_timeout(self):
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


def your_reaction_function():
    print("Directory has been unchanged for 10 minutes!")


if __name__ == "__main__":
    path = "/path/to/your/directory"
    app_name = "telegram"
    event_handler = ChangeHandler(timeout=600, reaction=your_reaction_function)  # 600 seconds = 10 minutes
    observer = Observer()

    observer_started = False

    try:
        while True:
            if is_app_running(app_name):
                if not observer_started:
                    observer = Observer()
                    observer.schedule(event_handler, path, rcursive=True)
                    observer.start()
                    observer_started = True
                    print(f"observer on path {path} started because {app_name} is running")
            elif observer_started:
                observer.stop()
                observer.join()
                observer_started = False
                print(f"observer stopped because {app_name} is not running")
            time.sleep(1)

    except KeyboardInterrupt:
        if observer_started:
            observer.stop()
            observer.join()
        print("Observer has been shut down")
