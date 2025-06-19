import logging
import os
from textual.logging import TextualHandler

LOG_PATH = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'dashboard.log')

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
    format='%(asctime)s %(levelname)s: %(message)s',
)


logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)
# logger.handlers.append(TextualHandler())
# logger.propagate = False

# if not logger.handlers:
#     file_handler = logging.FileHandler(LOG_PATH)
#     formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
