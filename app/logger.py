from loguru import logger
import os
from app.config import LOG_PATH

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger.remove()
logger.add(LOG_PATH, rotation="1 week", retention="4 weeks", level="INFO", encoding="utf-8")
logger.add(lambda msg: print(msg, end=""), level="INFO")
