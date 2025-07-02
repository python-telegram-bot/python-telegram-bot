import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
