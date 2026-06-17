
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

def setup_unified_logging():
    """
    Sets up a unified logging system that writes to the current app directory logs\\POS_SYSTEM.log
    and provides a consistent interface.
    """
    # Use the current directory where the application is running
    app_dir = Path.cwd()
    log_dir = app_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "POS_SYSTEM.log"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")
        # Fallback to current directory
        try:
            fallback_handler = logging.FileHandler("pos_system_fallback.log", mode='a')
            root_logger.addHandler(fallback_handler)
        except:
            pass
            
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    logging.info("="*80)
    logging.info(f"POS SYSTEM UNIFIED LOGGING INITIALIZED - {datetime.now()}")
    logging.info(f"Log File: {log_file}")
    logging.info("="*80)
    
    return root_logger

# Initialize on import
unified_logger = setup_unified_logging()
