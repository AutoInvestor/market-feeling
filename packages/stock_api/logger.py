import logging


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: str = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        record.levelname = f"{record.levelname}"
        record.name = f"{record.name}"
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
