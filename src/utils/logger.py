import logging
import sys
from typing import Optional


def setup_logger(
    name: str, level: int = logging.INFO, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Create a modular logger instance.

    :param name: Name of the logger
    :param level: Logging level (default: INFO)
    :param log_file: Optional file path to save logs
    :return: Configured logger object
    """
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers to the same logger
    if not logger.handlers:
        # Formatter: timestamp, level, logger name, message
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler: print logs to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Optional file handler: save logs to file
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Set logger level
        logger.setLevel(level)

    return logger


log = setup_logger("slack")
