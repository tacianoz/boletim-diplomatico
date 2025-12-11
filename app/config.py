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

# Ollama API (modelo local)
# Prioridade: 1) Variável de ambiente (docker-compose/env), 2) Detecção automática
_env_ollama_url = os.getenv('OLLAMA_API_URL')

# Se já está configurado via variável de ambiente, usar diretamente
if _env_ollama_url:
    OLLAMA_API_URL = _env_ollama_url
else:
    # Detecção automática: verifica se está rodando em Docker
    import os.path
    is_docker = False
    try:
        # Múltiplas formas de detectar se está no Docker
        if os.path.exists('/proc/self/cgroup'):
            with open('/proc/self/cgroup', 'r') as f:
                is_docker = any('docker' in line for line in f)
        # Verifica também se existe /.dockerenv (outra forma comum)
        if not is_docker:
            is_docker = os.path.exists('/.dockerenv')
    except (IOError, OSError):
        pass  # Se não conseguir ler, assume que não está no Docker
    
    # Define URL padrão baseado no ambiente
    if is_docker:
        OLLAMA_API_URL = 'http://host.docker.internal:11434/api/generate'
    else:
        OLLAMA_API_URL = 'http://localhost:11434/api/generate'

OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

# Google Gemini API (opcional, para fallback se necessário)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kolkata')

LOG_PATH = os.getenv('LOG_PATH', 'logs/boletim.log')

# URLs específicas para scraping
MEA_PRESS_RELEASES_URL = "https://www.mea.gov.in/press-releases.htm?51/Press_Releases"
MEA_MEDIA_BRIEFINGS_URL = "https://www.mea.gov.in/media-briefings.htm?49/Media_Briefings"
MEA_SPEECHES_URL = "https://www.mea.gov.in/Speeches-Statements.htm?50/Speeches__amp;_Statements"
PM_RELEASES_URL = "https://www.pib.gov.in/PMContents/PMContents.aspx?menuid=1&lang=1&reg=3" # URL with English language

# Configurações de scraping
SCRAPER_RETRY_ATTEMPTS = 3
SCRAPER_RETRY_DELAYS = [1, 2, 4]  # segundos
SCRAPER_TIMEOUT = 30
SELENIUM_WAIT_TIME = 3  # segundos para postbacks
