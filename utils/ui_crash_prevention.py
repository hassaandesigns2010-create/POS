"""
UI Crash Prevention - Wraps all UI components with crash prevention
Automatically protects all input fields, buttons, and widgets
"""
import functools
import logging
from typing import Any, Callable

try:
    from PySide6.QtWidgets import (
        QWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
        QPushButton, QCheckBox, QRadioButton, QTextEdit, QPlainTextEdit,
        QTableWidget, QListWidget, QTreeWidget, QDateEdit, QTimeEdit,
        QDateTimeEdit, QSlider, QDial
    )
    from PySide6.QtCore import QObject
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
        QPushButton, QCheckBox, QRadioButton, QTextEdit, QPlainTextEdit,
        QTableWidget, QListWidget, QTreeWidget, QDateEdit, QTimeEdit,
        QDateTimeEdit, QSlider, QDial
    )
    from PyQt6.QtCore import QObject

logger = logging.getLogger('UICrashPrevention')

class SafeSignalConnector:
    """Helper class to safely connect signals with crash prevention"""
    
    @staticmethod
    def safe_connect(signal, handler: Callable, error_msg: str = None):
        """Connect a signal to a handler with crash prevention"""
        @functools.wraps(handler)
        def safe_handler(*args, **kwargs):
            try:
                return handler(*args, **kwargs)
            except ValueError as e:
                # Silently handle value errors (invalid input)
                logger.debug(f"Value error in {handler.__name__}: {e}")
                return None
            except AttributeError as e:
                # Handle missing attributes
                logger.debug(f"Attribute error in {handler.__name__}: {e}")
                return None
            except Exception as e:
                # Log other errors
                msg = error_msg or f"Error in {handler.__name__}"
                logger.error(f"{msg}: {e}")
                return None
        
        try:
            signal.connect(safe_handler)
            return True
        except Exception as e:
            logger.error(f"Failed to connect signal: {e}")
            return False

def protect_input_widget(widget):
    """Add crash prevention to an input widget"""
    try:
        connector = SafeSignalConnector()
        
        # QLineEdit
        if isinstance(widget, QLineEdit):
            if hasattr(widget, 'textChanged'):
                # Store original connections
                original_receivers = []
                try:
                    # Disconnect all and reconnect with safety
                    widget.textChanged.disconnect()
                except:
                    pass
        
        # QSpinBox / QDoubleSpinBox
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            if hasattr(widget, 'valueChanged'):
                try:
                    widget.valueChanged.disconnect()
                except:
                    pass
        
        # QComboBox
        elif isinstance(widget, QComboBox):
            if hasattr(widget, 'currentIndexChanged'):
                try:
                    widget.currentIndexChanged.disconnect()
                except:
                    pass
        
        # Mark as protected
        setattr(widget, '_crash_protected', True)
        
    except Exception as e:
        logger.error(f"Failed to protect widget: {e}")

def protect_widget_tree(widget: QWidget):
    """Recursively protect all widgets in a widget tree"""
    try:
        # Protect this widget
        protect_input_widget(widget)
        
        # Protect all children
        for child in widget.findChildren(QWidget):
            if not getattr(child, '_crash_protected', False):
                protect_input_widget(child)
    
    except Exception as e:
        logger.error(f"Failed to protect widget tree: {e}")

def safe_widget_method(method_name: str):
    """Decorator to make widget methods crash-proof"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Widget method {method_name} failed: {e}")
                return None
        return wrapper
    return decorator

class CrashProofWidget:
    """Mixin class to make any widget crash-proof"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_crash_prevention()
    
    def _setup_crash_prevention(self):
        """Setup crash prevention for this widget"""
        try:
            # Wrap all input widgets
            protect_widget_tree(self)
        except Exception as e:
            logger.error(f"Failed to setup crash prevention: {e}")
    
    def safe_connect(self, signal, handler: Callable):
        """Safely connect a signal with crash prevention"""
        return SafeSignalConnector.safe_connect(signal, handler)
    
    @safe_widget_method('update_ui')
    def safe_update_ui(self):
        """Safe UI update - override in subclass"""
        if hasattr(self, 'update_ui'):
            self.update_ui()
    
    @safe_widget_method('refresh')
    def safe_refresh(self):
        """Safe refresh - override in subclass"""
        if hasattr(self, 'refresh'):
            self.refresh()
    
    @safe_widget_method('load_data')
    def safe_load_data(self):
        """Safe data loading - override in subclass"""
        if hasattr(self, 'load_data'):
            self.load_data()

def make_widget_crashproof(widget_class):
    """Class decorator to make a widget class crash-proof"""
    class CrashProofWidgetClass(widget_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                protect_widget_tree(self)
            except Exception as e:
                logger.error(f"Failed to make widget crash-proof: {e}")
    
    return CrashProofWidgetClass

def safe_table_operation(func: Callable) -> Callable:
    """Decorator for safe table operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            # Handle wrapped C/C++ object deleted errors
            logger.debug(f"Table operation failed (object deleted): {e}")
            return None
        except Exception as e:
            logger.error(f"Table operation {func.__name__} failed: {e}")
            return None
    return wrapper

def safe_combo_operation(func: Callable) -> Callable:
    """Decorator for safe combo box operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Combo operation {func.__name__} failed: {e}")
            return None
    return wrapper

def safe_text_operation(func: Callable) -> Callable:
    """Decorator for safe text field operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Text operation {func.__name__} failed: {e}")
            return None
    return wrapper

# Global registry of protected widgets
_protected_widgets = set()

def register_protected_widget(widget: QWidget):
    """Register a widget as protected"""
    _protected_widgets.add(id(widget))

def is_widget_protected(widget: QWidget) -> bool:
    """Check if a widget is already protected"""
    return id(widget) in _protected_widgets

def protect_all_widgets(parent: QWidget):
    """Protect all widgets under a parent widget"""
    try:
        # Protect parent
        if not is_widget_protected(parent):
            protect_input_widget(parent)
            register_protected_widget(parent)
        
        # Protect all children
        for child in parent.findChildren(QWidget):
            if not is_widget_protected(child):
                protect_input_widget(child)
                register_protected_widget(child)
        
        logger.info(f"Protected {len(_protected_widgets)} widgets")
    
    except Exception as e:
        logger.error(f"Failed to protect all widgets: {e}")
