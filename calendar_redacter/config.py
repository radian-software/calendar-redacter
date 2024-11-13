import dotenv

dotenv.load_dotenv()

import os
from pathlib import Path

CALDAV_URL = os.environ["CALDAV_URL"]
CALDAV_USERNAME = os.environ["CALDAV_USERNAME"]
CALDAV_PASSWORD = os.environ["CALDAV_PASSWORD"]
CALDAV_COLLECTIONS = os.environ["CALDAV_COLLECTIONS"].split(",")
CALDAV_REDACTED = os.environ["CALDAV_REDACTED"]

DATA_DIR = Path(__file__).parent.parent / "data"
