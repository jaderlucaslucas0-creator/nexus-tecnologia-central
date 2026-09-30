import os
from pathlib import Path

APP_NAME = "JARVIS AI"
VERSION = "0.2.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("JARVIS_DATA_DIR", str(BASE_DIR / "data")))
DATABASE_PATH = DATA_DIR / "jarvis.db"
