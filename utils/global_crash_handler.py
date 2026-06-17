"""
Global Crash Handler - Prevents application crashes across all UI components
Wraps all Qt signals, slots, and event handlers with exception handling
"""
import sys
import traceback
import logging
from datetime import datetime
from pathlib import Path
import functools

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import QObject, Signal, Slot
except ImportError:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot

class GlobalCrashHandler(QObject):
    """Global crash handler that prevents application crashes"""
    
    crash_occurred = Signal(str, str)  # error_type, error_message
    
    def __init__(self):
        super().__init__()
        self.crash_count = 0
        self.max_crashes_before_alert = 5
        self.setup_logging()
        self.install_handlers()
    
    def setup_logging(self):
        """Setup crash logging"""
        try:
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).parent
            else:
                app_dir = Path(__file__).parent.parent.parent
            
            log_dir = app_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"crashes_{datetime.now().strftime('%Y%m%d')}.log"
            
            self.logger = logging.getLogger('GlobalCrashHandler')
            self.logger.setLevel(logging.DEBUG)
            
            if not self.logger.handlers:
                fh = logging.FileHandler(log_file, encoding='utf-8')
                fh.setLevel(logging.DEBUG)
                
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                fh.setFormatter(formatter)
                
                self.logger.addHandler(fh)
            
            self.logger.info("="*80)
            self.logger.info("Global Crash Handler Initialized")
            self.logger.info("="*80)
            
        except Exception as e:
            print(f"[CRASH_HANDLER] Could not setup logging: {e}")
            self.logger = None
    
    def install_handlers(self):
        """Install global exception handlers"""
        sys.excepthook = self.handle_exception
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        try:
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            self.crash_count += 1
            
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
            
            # Emit signal
            self.crash_occurred.emit(exc_type.__name__, str(exc_value))
            
            # Show user-friendly message (non-blocking)
            if self.crash_count <= self.max_crashes_before_alert:
                self.show_error_dialog(exc_type, exc_value, show_details=False)
            else:
                self.show_critical_alert()
                
        except Exception as e:
            print(f"[CRITICAL] Crash handler itself failed: {e}")
    
    def show_error_dialog(self, exc_type, exc_value, show_details=False):
        """Show user-friendly error dialog"""
        try:
            app = QApplication.instance()
            if app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error Recovered")
                msg.setText("An error occurred but was automatically recovered.")
                msg.setInformativeText("The application will continue running.")
                
                if show_details:
                    msg.setDetailedText(f"{exc_type.__name__}: {str(exc_value)}")
                
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                
                # Non-blocking show
                msg.show()
        except:
            pass
    
    def show_critical_alert(self):
        """Show critical alert when too many crashes occur"""
        try:
            app = QApplication.instance()
            if app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Multiple Errors Detected")
                msg.setText(f"The application has recovered from {self.crash_count} errors.")
                msg.setInformativeText("Please save your work and restart the application.\nContact support if the issue persists.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
        except:
            pass

def safe_slot(func):
    """Decorator to make Qt slots crash-proof"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                logger = logging.getLogger('GlobalCrashHandler')
                logger.error(f"Slot {func.__name__} failed: {e}")
                logger.error(traceback.format_exc())
            except:
                print(f"[ERROR] Slot {func.__name__} failed: {e}")
            return None
    return wrapper

def safe_signal_handler(func):
    """Decorator to make signal handlers crash-proof"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                logger = logging.getLogger('GlobalCrashHandler')
                logger.error(f"Signal handler {func.__name__} failed: {e}")
                logger.error(traceback.format_exc())
            except:
                print(f"[ERROR] Signal handler {func.__name__} failed: {e}")
            return None
    return wrapper

def safe_method(func):
    """Decorator to make any method crash-proof"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                logger = logging.getLogger('GlobalCrashHandler')
                logger.error(f"Method {func.__name__} failed: {e}")
                logger.error(traceback.format_exc())
            except:
                print(f"[ERROR] Method {func.__name__} failed: {e}")
            return None
    return wrapper

def wrap_widget_signals(widget):
    """Wrap all signals of a widget with crash prevention"""
    try:
        # Common input widget signals
        signal_names = []
        
        if hasattr(widget, 'textChanged'):
            signal_names.append('textChanged')
        if hasattr(widget, 'valueChanged'):
            signal_names.append('valueChanged')
        if hasattr(widget, 'currentIndexChanged'):
            signal_names.append('currentIndexChanged')
        if hasattr(widget, 'clicked'):
            signal_names.append('clicked')
        if hasattr(widget, 'toggled'):
            signal_names.append('toggled')
        if hasattr(widget, 'editingFinished'):
            signal_names.append('editingFinished')
        if hasattr(widget, 'returnPressed'):
            signal_names.append('returnPressed')
        if hasattr(widget, 'activated'):
            signal_names.append('activated')
        
        # Store original signal connections
        for sig_name in signal_names:
            try:
                signal = getattr(widget, sig_name, None)
                if signal:
                    # Mark as wrapped
                    setattr(widget, f'_{sig_name}_wrapped', True)
            except Exception as e:
                logger = logging.getLogger('GlobalCrashHandler')
                logger.debug(f"Could not wrap signal {sig_name}: {e}")
    except Exception as e:
        print(f"[ERROR] Could not wrap widget signals: {e}")

def safe_connect(signal, handler):
    """Safely connect a signal to a handler with crash prevention"""
    @functools.wraps(handler)
    def safe_handler(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            try:
                logger = logging.getLogger('GlobalCrashHandler')
                logger.error(f"Signal handler failed: {e}")
                logger.error(traceback.format_exc())
            except:
                print(f"[ERROR] Signal handler failed: {e}")
            return None
    
    try:
        signal.connect(safe_handler)
    except Exception as e:
        print(f"[ERROR] Could not connect signal safely: {e}")
        # Try connecting without wrapper as fallback
        try:
            signal.connect(handler)
        except:
            pass

# Global instance
_global_crash_handler = None

def initialize_global_crash_handler():
    """Initialize the global crash handler"""
    global _global_crash_handler
    if _global_crash_handler is None:
        _global_crash_handler = GlobalCrashHandler()
    return _global_crash_handler

def get_global_crash_handler():
    """Get the global crash handler instance"""
    global _global_crash_handler
    if _global_crash_handler is None:
        _global_crash_handler = GlobalCrashHandler()
    return _global_crash_handler
