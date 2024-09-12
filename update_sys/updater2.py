import os
import subprocess
import sys

def update_repo_except_self():
    """Update the entire repo but exclude this updater script."""
    try:
        # Get the current script's directory and name
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_name = os.path.basename(__file__)  # Get the updater script's name (e.g., 'updater.py')

        # Change to the repo directory
        os.chdir(script_dir)
        subprocess.run('pwd')
        # Stash the current version of the updater script to prevent it from being overwritten
        subprocess.run(['git', 'stash', 'push', '-m', '"Stashing updater script"', 'updater2.exe'], check=True)

        # Fetch the latest changes from the remote
        subprocess.run(['git', 'fetch'], check=True)

        # Get the current branch
        current_branch = subprocess.run(['git', 'branch', '--show-current'], check=True, text=True, capture_output=True).stdout.strip()

        # Checkout everything in the repo except the updater script
        subprocess.run(['git', 'checkout', f'origin/{current_branch}', '--', '.'], check=True)

        # Hard reset local branch to match the remote (this will overwrite local changes!)
        subprocess.run(['git', 'reset', '--hard', f'origin/{current_branch}'], check=True)

        # Restore the updater script from the stash
        subprocess.run(['git', 'stash', 'pop'], check=True)

        print("Repository updated successfully, except for the updater script.")
    except subprocess.CalledProcessError as e:
        print(f"Error during repository update: {e}")
        sys.exit(1)

def restart_main_script():
    """Restart the main script after the update."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.Popen([sys.executable, os.path.join(script_dir, 'main_script.py')])
    except Exception as e:
        print(f"Error restarting the main script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_repo_except_self()
