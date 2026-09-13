import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables from .env file
admins_ids_str = os.getenv("ADMINS_IDS")
if admins_ids_str is not None:
    admins_ids_str = map(int, admins_ids_str.split(","))

ADMINS_IDS = list(admins_ids_str)

BOT_TOKEN = os.getenv("BOT_TOKEN")

WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8080))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

DATABASE_URL = os.getenv("DATABASE_URL")

# Image paths
GARANT_PHOTO_PATH = "images/garant.jpg"
TRUSTED_GARANT_PHOTO_PATH = "images/trusted_garant.jpg"
SCAM_PHOTO_PATH = "images/scam.jpg"
USER_PHOTO_PATH = "images/user.jpg"

# User types
USER_TYPE_USER = "Обычный пользователь"
USER_TYPE_SCAMMER = "Скаммер"
USER_TYPE_GARANT = "Гарант"
USER_TYPE_TRUSTED_GARANT = "Проверенный гарант"

POST_COLORS = ("danger", "success", "primary")