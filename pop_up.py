import tkinter as tk
from tkinter import messagebox
import os
from config_setup import setup_config


paths, app_settings, pushover_credentials, scanner = setup_config()
message_file = paths['message_file']


def show_pop_up(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Ensure it is on top
    messagebox.showinfo("Scanner Inactivity", message)
    root.destroy()


if __name__ == "__main__":

    if os.path.exists(message_file):
        with open(message_file, "r") as m:
            message = m.read().strip()
        if message:
            show_pop_up(message)
        else:
            print("Message file is empty.")
    else:
        print(f"{message_file} does not exist.")
