# Configure local logger
# Enable logging, this will also direct built-in DXL log messages.
# See - https://docs.python.org/2/howto/logging-cookbook.html

import logging


log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)