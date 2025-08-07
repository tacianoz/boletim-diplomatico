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

TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')

LOG_PATH = os.getenv('LOG_PATH', 'logs/boletim.log')
