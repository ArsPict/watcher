import time
import subprocess
import logging

# Set up logging to track when the service triggers notifications
logging.basicConfig(filename='service_log.log', level=logging.INFO)

def inactivity_pop_up():
    try:
        print("trying")
        # Trigger the Windows Task Scheduler to run the task
        subprocess.run(['schtasks', '/run', '/tn', 'pop_up_test'], check=True)
        logging.info("Inactivity notification triggered at %s", time.ctime())
    except subprocess.CalledProcessError as e:
        print("errror")
        logging.error("Error triggering Task Scheduler: %s", str(e))

if __name__ == "__main__":
    print("start")
    inactivity_pop_up()
    a = 1
    while True:
        a = a + 1
