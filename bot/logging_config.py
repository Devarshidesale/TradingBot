import os
import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger("trading_bot")

    # Avoid adding duplicate handlers if called more than once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"

    # File handler — DEBUG level (captures everything)
    log_path = os.path.join(os.path.dirname(__file__), "..", "trading_bot.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler — INFO level (only important messages)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
