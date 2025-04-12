import logging
import os
from typing import Dict, Optional, Union
import sys

# Global dictionary to store loggers
_loggers: Dict[str, logging.Logger] = {}

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Set environment variables immediately when this module is imported
# This ensures it happens before any other imports
os.environ["BROWSER_USE_LOGGING_LEVEL"] = "error"  # Use error instead of warning for more strict filtering

# Monkey patch the logging module to intercept browser_use logs
original_getLogger = logging.getLogger

def patched_getLogger(name=None):  # Make name parameter optional
    logger = original_getLogger(name)
    if name in ["browser_use", "root"] or name is None:
        logger.setLevel(logging.ERROR)
        # Replace handlers to ensure our level setting takes effect
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
    return logger

logging.getLogger = patched_getLogger


def setup_logging(default_level: int = DEFAULT_LOG_LEVEL) -> None:
    """
    Setup basic logging configuration for the application.
    
    :param default_level: Default logging level for all loggers
    """
    # Configure root logger
    logging.basicConfig(
        level=default_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Disable unwanted loggers with stronger settings
    for logger_name in ["browser_use", "httpx", "httpcore", "urllib3", "requests", "root"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)
        # Make propagate False to prevent logs from propagating to parent loggers
        logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    :param name: Name of the logger
    :return: Logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]


def set_log_level(logger_name: str, level: Union[int, str]) -> None:
    """
    Set the log level for a specific logger.
    
    :param logger_name: Name of the logger
    :param level: Log level (can be int constant or string name)
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Get the logger and set its level
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Special handling for browser_use package
    if logger_name == "browser_use":
        level_name = logging.getLevelName(level).lower()
        os.environ["BROWSER_USE_LOGGING_LEVEL"] = level_name


def get_log_level_from_env(logger_name: str, default_level: int = DEFAULT_LOG_LEVEL) -> int:
    """
    Get log level from environment variable.
    
    :param logger_name: Name of the logger
    :param default_level: Default level if environment variable is not set
    :return: Log level
    """
    env_var = f"LOG_LEVEL_{logger_name.upper()}"
    level_str = os.environ.get(env_var)
    
    if level_str:
        try:
            return getattr(logging, level_str.upper())
        except AttributeError:
            # Invalid log level name, use default
            pass
    
    return default_level


def disable_third_party_loggers() -> None:
    """
    Disable common third-party loggers that might be too verbose.
    """
    third_party_loggers = [
        "browser_use",
        "httpx",
        "httpcore",
        "urllib3",
        "requests",
        "root"  # Also disable the root logger from browser_use
    ]
    
    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        # Special handling for browser_use
        if logger_name == "browser_use":
            os.environ["BROWSER_USE_LOGGING_LEVEL"] = "error" 