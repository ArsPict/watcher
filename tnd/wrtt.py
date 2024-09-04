import time
import logging

# Configure logging
logging.basicConfig(
    filename=r"C:\temp\service_log.txt",  # Make sure this directory exists
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def main():
    logging.info("Service has started.")
    try:
        while True:
            logging.info("Service is running...")
            time.sleep(10)  # Wait for 10 seconds before the next log entry
    except Exception as e:
        logging.error(f"Service encountered an error: {e}")
    finally:
        logging.info("Service is stopping.")

if __name__ == "__main__":
    main()