import logging
from logging.handlers import RotatingFileHandler


def get_logger(
    name: str = __name__,
    logfile: str = "market_feeling.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Returns a logger that writes to both stdout and a rotating log file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        fmt = logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s - %(message)s")

        # File handler (rotates at max_bytes, keeps backup_count files)
        fh = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
