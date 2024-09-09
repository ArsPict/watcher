import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Create handler with file rotation
handler = RotatingFileHandler('./app.log', maxBytes=2000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

# Example log messages
for i in range(1000):
    logger.info(f"This is log message {i}")