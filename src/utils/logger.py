"""Centralized logging configuration."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config.constants import LOGS_DIR

_logger_initialized = False


def setup_logging(level: int = logging.INFO) -> None:
    """
    Initialize logging configuration.
    
    Args:
        level: Logging level (default: INFO)
    """
    global _logger_initialized
    
    if _logger_initialized:
        return
    
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOGS_DIR / f"{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    _logger_initialized = True
    
    logging.info(f"Logging initialized. Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
