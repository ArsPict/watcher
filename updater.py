import os
import subprocess


service_name = "watcher.exe"

def replace_w_latest_updates():
    # Change to the script's directory where the local git repo exists
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Ensure script_dir is defined
    os.chdir(script_dir)

    # Fetch the latest updates from the remote
    subprocess.run(['git', 'fetch'], check=True)

    # Update only the .gitignore file with the remote version
    subprocess.run(['git', 'checkout', 'origin/main', '--', '.gitignore'], check=True)

    # Hard reset local branch to match the remote (this will overwrite local changes!)
    subprocess.run(['git', 'reset', '--hard', 'origin/main'], check=True)

    print("Local repository successfully updated with latest remote changes.")


def stop_service(service_name):
    """Stop the service before pulling updates."""
    print(f"Stopping the service: {service_name}")
    subprocess.run(['sc', 'stop', service_name], check=True)


def start_service(service_name):
    """Start the service after pulling updates."""
    print(f"Starting the service: {service_name}")
    subprocess.run(['sc', 'start', service_name], check=True)


if __name__ == "__main__":
    replace_w_latest_updates()
