import configparser
import os
import sys


def setup_config():

    if getattr(sys, 'frozen', False):
        # When run as an .exe (compiled with PyInstaller), use the exe's directory
        script_dir = os.path.dirname(sys.executable)
    else:
        # When running as a .py script, use the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

    config_file = os.path.join(script_dir, 'config.ini')
    config = configparser.ConfigParser()

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} does not exist.")

    config.read(config_file)

    paths = {
        'dirs': config.get('Paths', 'dirs').split(','),
        'message_file': config.get('Paths', 'message_file'),
        'last_mod_file': config.get('Paths', 'last_mod_file')
    }

    app_settings = {
        'app_name': config.get('App', 'app_name'),
        'inactivity_duration': config.getint('App', 'inactivity_duration'),
        'tick': config.getint('App', 'tick')
    }

    pushover = {
        'USER_KEY': config.get('Pushover', 'USER_KEY'),
        'APP_TOKEN': config.get('Pushover', 'APP_TOKEN'),
        'send_notification': config.get('Pushover', 'send_notification')
    }

    scanner = {
        'name': config.get('Scanner', 'name')
    }

    return paths, app_settings, pushover, scanner


# Example usage
if __name__ == "__main__":
    try:
        paths, app_settings, pushover, scanner = setup_config()

        # Access the constants
        print("Paths:", paths)
        print("App Settings:", app_settings)
        print("Pushover:", pushover)

    except Exception as e:
        print(f"Error: {str(e)}")