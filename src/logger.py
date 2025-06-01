import logging
import os

LOG_PATH = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'dashboard.log')

logger = logging.getLogger('dashboard')
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
