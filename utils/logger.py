import logging
import os
from datetime import datetime

def setup_logger(name, log_dir="logs"):
    """Set up a logger with file and console handlers"""
    # Try to use user's Documents folder if Program Files is not writable
    if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
        # Use current directory if writable
        pass
    else:
        # Use user's Documents folder
        try:
            import pathlib
            documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
            log_dir = os.path.join(documents_dir, "POS_Offline", "logs")
        except Exception:
            # Fallback to temp directory
            import tempfile
            log_dir = os.path.join(tempfile.gettempdir(), "POS_Offline", "logs")
    
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except PermissionError:
            # If we still can't create logs directory, disable file logging
            log_dir = None

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler (only if log_dir is available)
    if log_dir is not None:
        try:
            log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue with console only
            pass

    # Console handler (always available)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger

def get_logger(name=None):
    """Get or create a logger instance"""
    if name is None:
        name = 'pos_app'
    return setup_logger(name)

# Create loggers for different modules
app_logger = setup_logger('app')
db_logger = setup_logger('database')
sales_logger = setup_logger('sales')
inventory_logger = setup_logger('inventory')
