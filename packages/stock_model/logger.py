import logging


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Initialize and return a logger with a specified name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Only add a handler if the logger has no handlers (avoid duplicate messages)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
