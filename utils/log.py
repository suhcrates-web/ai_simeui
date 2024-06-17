import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger():
    log_directory = Path(__file__).parents[1] / 'log'
    log_file = "chat.log"

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_path = os.path.join(log_directory, log_file)

    logger = logging.getLogger('chat_logger')
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(log_path, maxBytes=1048576, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - Conversation ID: %(conversation_id)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
