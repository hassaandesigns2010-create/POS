
"""
Robust Error Handling System
Prevents application crashes and provides graceful error recovery
"""
import sys
import os
import traceback
import logging
import functools
import time
from datetime import datetime

class BulletproofErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.max_errors = 50
        self.setup_logging()
        self.install_global_handler()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        try:
            # Try to create logs directory in app folder first
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            log_dir = os.path.join(app_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"pos_errors_{datetime.now().strftime('%Y%m%d')}.log")
            
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger('POS_System')
            self.logger.info("POS System starting - Error handler initialized")
            
        except Exception as e:
            print(f"[ERROR_HANDLER] Could not setup logging: {e}")
    
    def install_global_handler(self):
        """Install global exception handler"""
        sys.excepthook = self.handle_exception
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle any unhandled exception"""
        try:
            error_msg = f"UNHANDLED EXCEPTION: {exc_type.__name__}: {exc_value}"
            self.logger.error(error_msg)
            self.logger.error("Traceback:", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Show user-friendly error
            self.show_user_error(error_msg)
            
        except Exception as e:
            print(f"[CRITICAL] Error handler failed: {e}")
        
        # Don't crash - try to continue
        return True
    
    def show_user_error(self, error_msg):
        """Show user-friendly error message"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            if QApplication.instance():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("POS System Error")
                msg.setText("An error occurred, but the system will continue running.")
                msg.setDetailedText(error_msg)
                msg.exec()
        except:
            print(f"[ERROR] {error_msg}")
    
    def safe_execute(self, func, *args, **kwargs):
        """Safely execute any function"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Safe execution failed for {func.__name__}: {e}")
            return None

# Global error handler
_error_handler = BulletproofErrorHandler()
safe_execute = _error_handler.safe_execute

def safe_function(func):
    """Decorator to make any function safe from crashes"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                _error_handler.logger.error(f"Safe function {func.__name__} failed: {e}")
            except:
                print(f"[ERROR] {func.__name__} failed: {e}")
            return None
    return wrapper

def handle_database_errors(func):
    """Decorator to handle database-specific errors gracefully"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if 'connection' in error_msg or 'database' in error_msg or 'psycopg2' in error_msg:
                try:
                    _error_handler.logger.error(f"Database error in {func.__name__}: {e}")
                except:
                    print(f"[DB ERROR] {func.__name__}: {e}")
            else:
                try:
                    _error_handler.logger.error(f"Error in {func.__name__}: {e}")
                except:
                    print(f"[ERROR] {func.__name__}: {e}")
            return None
    return wrapper
