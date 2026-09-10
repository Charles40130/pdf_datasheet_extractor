import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
PREFERRED_SITE = (os.getenv("PREFERRED_SITE") or "cedeo").lower()
CEDEO_EMAIL = os.getenv("CEDEO_EMAIL")
CEDEO_PASSWORD = os.getenv("CEDEO_PASSWORD")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "input")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "output")
COOKIE_DIR = os.path.join(PROJECT_ROOT, "data", "cookies")
CHROME_PROFILE_DIR = os.path.join(PROJECT_ROOT, "data", "chrome_profile")
CEDEO_COOKIES_FILE = os.path.join(COOKIE_DIR, "cedeo_cookies.json")
