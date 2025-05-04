import logging
import sys


class GCPConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return f"{record.levelname} {record.name} - {record.getMessage()}"


def get_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = GCPConsoleFormatter()

    # DEBUG / INFO / WARNING → stdout  → blue ℹ️ in Cloud Logging
    out_handler = logging.StreamHandler(sys.stdout)
    out_handler.setLevel(logging.DEBUG)
    out_handler.addFilter(lambda r: r.levelno < logging.ERROR)
    out_handler.setFormatter(formatter)

    # ERROR / CRITICAL → stderr → red ❗ in Cloud Logging
    err_handler = logging.StreamHandler(sys.stderr)
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)

    logger.addHandler(out_handler)
    logger.addHandler(err_handler)
    logger.propagate = False

    return logger
