"""
Logging configuration for the Medical Diagnostics System.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory (with error handling for deployment environments)
LOGS_DIR = Path(__file__).parent.parent / "logs"
try:
    LOGS_DIR.mkdir(exist_ok=True)
except (PermissionError, OSError):
    # Fallback to /tmp on systems where project directory isn't writable
    import tempfile
    LOGS_DIR = Path(tempfile.gettempdir()) / "medical_diagnostics_logs"
    LOGS_DIR.mkdir(exist_ok=True)

# Log file with timestamp
LOG_FILE = LOGS_DIR / f"medical_diagnostics_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logger(name: str = "medical_diagnostics", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger for the application.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (with error handling for deployment environments)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        # If file logging fails (e.g., in restricted deployment environments),
        # continue with console logging only
        pass
    
    # Console handler (always available)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()

