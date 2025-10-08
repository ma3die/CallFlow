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
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")
UPLOAD = Path(os.getenv("UPLOAD_DIR"))
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / UPLOAD

APP_PATH = 'src.core.app:app'
