"""
Logging utility for the data warehouse migration utility.
"""
import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_dir: str = "output/logs", log_level: str = "INFO") -> None:
    """
    Configure the logger for the application.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Add file handler for all logs
    logger.add(
        log_path / "migration_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    # Add file handler for errors only
    logger.add(
        log_path / "errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )

    logger.info("Logger initialized successfully")


def get_logger():
    """
    Get the configured logger instance.

    Returns:
        Logger instance
    """
    return logger
