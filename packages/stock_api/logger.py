import logging

RESET = "\033[0m"
LEVEL_COLORS = {
    logging.DEBUG:    "\033[36m",  # Cyan
    logging.INFO:     "\033[32m",  # Green
    logging.WARNING:  "\033[33m",  # Yellow
    logging.ERROR:    "\033[31m",  # Red
    logging.CRITICAL: "\033[1;31m" # Bold Red
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: str = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, RESET)
        record.levelname = f"{color}{record.levelname}{RESET}"
        record.name      = f"{record.name}"
        return super().format(record)

def get_logger(
    name: str = __name__,
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        fmt = "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(ColoredFormatter(fmt, datefmt))
        logger.addHandler(ch)

    return logger
