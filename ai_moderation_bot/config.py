import bcrypt
import logging
from dotenv import load_dotenv
import os

JWT_SECRET = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2Mj"
              "M5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
KEY = b'$2b$12$G4Z3Q731NuLWY0EH8dRahe'
ALGORITHM = "HS256"

load_dotenv()

try:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CREDENTIALS = os.getenv("CREDENTIALS_AI")
    VERTEX_AI_ID = os.getenv("VERTEX_AI_ID")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logging.error("Environment variable DATABASE_URL is not set or is empty")
        raise ValueError("Environment variable DATABASE_URL is not set or is empty")
except ValueError as v:
    logging.error(f"Environment variable is not set, {v}")