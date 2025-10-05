from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))

APP_PATH = 'src.core.app:app'
