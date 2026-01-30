"""
GeoLogix AI - Logging Configuration
Centralized logging setup for all modules.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Log directory
try:
    from Configuration.config import LOGS_DIR
except ImportError:
    # Fallback for manual script execution or if sys.path is weird
    LOG_DIR = Path(__file__).resolve().parent.parent / "Data_Directories" / "logs"
else:
    LOG_DIR = LOGS_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file with date
LOG_FILE = LOG_DIR / f"geologix_{datetime.now().strftime('%Y%m%d')}.log"

# Formatter
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(level: str = "INFO"):
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)

# Auto-setup on import
_logger = setup_logging()
