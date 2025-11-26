import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')

MODEL_PATH = os.getenv('MODEL_PATH')
MODEL_NAME = os.getenv('MODEL_NAME')

# Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kolkata')

LOG_PATH = os.getenv('LOG_PATH', 'logs/boletim.log')

# URLs específicas para scraping
MEA_PRESS_RELEASES_URL = "https://www.mea.gov.in/press-releases.htm?51/Press_Releases"
MEA_MEDIA_BRIEFINGS_URL = "https://www.mea.gov.in/media-briefings.htm?49/Media_Briefings"
MEA_SPEECHES_URL = "https://www.mea.gov.in/Speeches-Statements.htm?50/Speeches__amp;_Statements"
PM_RELEASES_URL = "https://www.pib.gov.in/PMContents/PMContents.aspx?menuid=1"

# Configurações de scraping
SCRAPER_RETRY_ATTEMPTS = 3
SCRAPER_RETRY_DELAYS = [1, 2, 4]  # segundos
SCRAPER_TIMEOUT = 30
SELENIUM_WAIT_TIME = 3  # segundos para postbacks
