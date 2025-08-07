import logging
from logging.handlers import RotatingFileHandler

# Налаштування RotatingFileHandler:
log_handler = RotatingFileHandler(
    "bot.log",            # ім'я основного файлу логу
    maxBytes=5_000_000,   # максимум ~5 MB (можна змінити)
    backupCount=3,        # зберігати останні 3 файли (bot.log.1, bot.log.2, bot.log.3)
    encoding="utf-8"
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def log_info(msg):
    logger.info(msg)

def log_error(msg):
    logger.error(msg)
