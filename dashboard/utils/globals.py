from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
# Load environment variables from .env file

# check that api URL and api key are set
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
if not API_URL or not API_KEY:
    raise ValueError("API_URL and API_KEY must be set in the .env file")
