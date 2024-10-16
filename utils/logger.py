import os
import time
import json
import logging
from typing import Dict, List

CONSOLE_LOGS = False
os.makedirs("./logs", exist_ok=True)

def get_logger(
    name: str,
    see_time: bool = False,
    console_log: bool = False,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Returns a logger object

    Args:
        name (str): Name of the logger
        level (int): Logging level
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if see_time:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = logging.Formatter("%(message)s,")

    file_handler = logging.FileHandler(f"./logs/{name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_log:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def log_message(
    message: str, logger: logging.Logger, level: int = logging.INFO
) -> None:
    """
    Logs a message

    Args:
        message (str): Message to be logged
        logger (logging.Logger): Logger object
        level (int): Logging level
    """
    if level == logging.INFO:
        logger.info(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.DEBUG:
        logger.debug(message)
    else:
        logger.info(message)

def time_logger(func):
    """
    Decorator that logs the execution time of a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    def wrapper(*args, **kwargs):
        logger = get_logger(
            func.__name__ + "_time_log", see_time=True, console_log=CONSOLE_LOGS
        )
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        log_message(
            f"Function {func.__name__} from {func.__qualname__} took {elapsed_time:.4f} seconds to run.", logger
        )
        return result

    return wrapper