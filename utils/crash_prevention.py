"""
Enhanced Crash Prevention System
Prevents application crashes on client PCs with automatic recovery
"""
import sys
import os
import traceback
import logging
from datetime import datetime
from pathlib import Path
import functools

class CrashPrevention:
    """Comprehensive crash prevention and recovery system"""
    
    def __init__(self):
        self.crash_count = 0
        self.max_crashes_before_alert = 10
        self.setup_logging()
        self.install_handlers()
    
    def setup_logging(self):
        """Setup crash logging"""
        try:
            # Create logs directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            log_dir = os.path.join(app_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Create crash log file
            crash_log = os.path.join(log_dir, f"crashes_{datetime.now().strftime('%Y%m%d')}.log")
            
            # Setup logger
            self.logger = logging.getLogger('CrashPrevention')
            self.logger.setLevel(logging.DEBUG)
            
            # File handler
            fh = logging.FileHandler(crash_log, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.WARNING)
            
            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
            
            self.logger.info("="*80)
            self.logger.info("Crash Prevention System Initialized")
            self.logger.info("="*80)
            
        except Exception as e:
            print(f"[CRASH_PREVENTION] Could not setup logging: {e}")
            self.logger = None
    
    def install_handlers(self):
        """Install global exception handlers"""
        sys.excepthook = self.handle_uncaught_exception
    
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions to prevent crashes"""
        try:
            # Skip keyboard interrupt
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            self.crash_count += 1
            
            # Log the error
            error_msg = f"UNCAUGHT EXCEPTION #{self.crash_count}"
            trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            
            if self.logger:
                self.logger.error(f"\n{'='*80}")
                self.logger.error(error_msg)
                self.logger.error(f"Type: {exc_type.__name__}")
                self.logger.error(f"Message: {exc_value}")
                self.logger.error(f"Traceback:\n{trace}")
                self.logger.error(f"{'='*80}\n")
            else:
                print(f"\n[ERROR] {error_msg}")
                print(f"Type: {exc_type.__name__}")
                print(f"Message: {exc_value}")
                print(trace)
            
            # Show user-friendly message
            self.show_error_dialog(exc_type, exc_value)
            
            # If too many crashes, alert user
            if self.crash_count >= self.max_crashes_before_alert:
                self.show_critical_alert()
                
        except Exception as e:
            print(f"[CRITICAL] Crash handler itself failed: {e}")
    
    def show_error_dialog(self, exc_type, exc_value):
        """Show user-friendly error dialog"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            if QApplication.instance():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error Recovered")
                msg.setText("An error occurred but was automatically recovered.")
                msg.setInformativeText(f"Error: {exc_type.__name__}\n{str(exc_value)}")
                msg.setDetailedText(f"The application will continue running.\n\nIf this error persists, please contact support.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
        except:
            pass
    
    def show_critical_alert(self):
        """Show critical alert when too many crashes occur"""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            
            if QApplication.instance():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Multiple Errors Detected")
                msg.setText(f"The application has recovered from {self.crash_count} errors.")
                msg.setInformativeText("Please restart the application and contact support if the issue persists.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
        except:
            pass

def safe_method(func):
    """Decorator to make any method crash-proof"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                # Try to log the error
                logger = logging.getLogger('CrashPrevention')
                logger.error(f"Safe method {func.__name__} failed: {e}")
                logger.error(traceback.format_exc())
            except:
                print(f"[ERROR] {func.__name__} failed: {e}")
            
            # Return None or appropriate default
            return None
    return wrapper

def safe_qt_slot(func):
    """Decorator specifically for Qt slots to prevent crashes"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                logger = logging.getLogger('CrashPrevention')
                logger.error(f"Qt slot {func.__name__} failed: {e}")
                logger.error(traceback.format_exc())
                
                # Show error to user
                from PySide6.QtWidgets import QMessageBox, QApplication
                if QApplication.instance():
                    QMessageBox.warning(
                        None,
                        "Operation Failed",
                        f"An error occurred: {str(e)}\n\nThe application will continue running."
                    )
            except:
                print(f"[ERROR] Qt slot {func.__name__} failed: {e}")
            
            return None
    return wrapper

# Global instance
_crash_prevention = None

def initialize_crash_prevention():
    """Initialize the global crash prevention system"""
    global _crash_prevention
    if _crash_prevention is None:
        _crash_prevention = CrashPrevention()
    return _crash_prevention

def get_crash_prevention():
    """Get the global crash prevention instance"""
    global _crash_prevention
    if _crash_prevention is None:
        _crash_prevention = CrashPrevention()
    return _crash_prevention
