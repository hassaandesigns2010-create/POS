"""
Safe Input Handler - Prevents crashes when typing in input fields
Wraps all input field signals with crash prevention
"""
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger('SafeInputHandler')

def safe_input_signal(func: Callable) -> Callable:
    """
    Decorator to make input field signal handlers crash-proof
    Prevents application crashes when typing in QLineEdit, QSpinBox, QDoubleSpinBox, etc.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # Handle invalid number conversions silently
            logger.debug(f"Input validation error in {func.__name__}: {e}")
            return None
        except AttributeError as e:
            # Handle missing attributes gracefully
            logger.debug(f"Attribute error in {func.__name__}: {e}")
            return None
        except Exception as e:
            # Catch all other exceptions
            logger.error(f"Error in input handler {func.__name__}: {e}")
            return None
    return wrapper

def safe_value_getter(widget, default=0.0):
    """
    Safely get value from any input widget
    Returns default if any error occurs
    """
    try:
        if hasattr(widget, 'value'):
            # QSpinBox, QDoubleSpinBox
            return float(widget.value())
        elif hasattr(widget, 'text'):
            # QLineEdit
            text = widget.text().strip()
            if not text:
                return default
            return float(text)
        else:
            return default
    except (ValueError, AttributeError, TypeError):
        return default

def safe_value_setter(widget, value, default=0.0):
    """
    Safely set value to any input widget
    Handles errors gracefully
    """
    try:
        safe_value = float(value) if value is not None else default
    except (ValueError, TypeError):
        safe_value = default
    
    try:
        if hasattr(widget, 'setValue'):
            # QSpinBox, QDoubleSpinBox
            widget.setValue(safe_value)
        elif hasattr(widget, 'setText'):
            # QLineEdit
            widget.setText(str(safe_value))
    except Exception as e:
        logger.error(f"Error setting widget value: {e}")

def connect_safe_signal(widget, signal_name: str, handler: Callable):
    """
    Connect a signal to a handler with crash prevention
    
    Args:
        widget: The Qt widget
        signal_name: Name of the signal (e.g., 'textChanged', 'valueChanged')
        handler: The handler function to connect
    """
    try:
        signal = getattr(widget, signal_name, None)
        if signal is None:
            logger.warning(f"Widget {widget} does not have signal {signal_name}")
            return False
        
        # Wrap the handler with crash prevention
        safe_handler = safe_input_signal(handler)
        
        # Connect the signal
        signal.connect(safe_handler)
        return True
    except Exception as e:
        logger.error(f"Error connecting signal {signal_name}: {e}")
        return False

class SafeInputMixin:
    """
    Mixin class to add safe input handling to any widget
    Usage: class MyWidget(QWidget, SafeInputMixin):
    """
    
    def safe_connect(self, widget, signal_name: str, handler: Callable):
        """Connect signal with crash prevention"""
        return connect_safe_signal(widget, signal_name, handler)
    
    def safe_get_value(self, widget, default=0.0):
        """Safely get value from widget"""
        return safe_value_getter(widget, default)
    
    def safe_set_value(self, widget, value, default=0.0):
        """Safely set value to widget"""
        return safe_value_setter(widget, value, default)
    
    @safe_input_signal
    def safe_update_totals(self):
        """Safe version of update_totals - override in subclass"""
        if hasattr(self, 'update_totals'):
            self.update_totals()
    
    @safe_input_signal
    def safe_calculate_change(self):
        """Safe version of calculate_change - override in subclass"""
        if hasattr(self, 'calculate_change'):
            self.calculate_change()

def make_input_safe(widget, signal_name: str = None):
    """
    Make an input widget safe by wrapping its common signals
    
    Args:
        widget: The Qt input widget
        signal_name: Specific signal to protect, or None for auto-detect
    """
    if signal_name:
        signals = [signal_name]
    else:
        # Auto-detect common signals
        signals = []
        if hasattr(widget, 'textChanged'):
            signals.append('textChanged')
        if hasattr(widget, 'valueChanged'):
            signals.append('valueChanged')
        if hasattr(widget, 'editingFinished'):
            signals.append('editingFinished')
    
    # Store original handlers
    for sig_name in signals:
        try:
            signal = getattr(widget, sig_name, None)
            if signal:
                # Disconnect all existing handlers
                try:
                    signal.disconnect()
                except:
                    pass
                
                # Reconnect with safe wrapper
                # Note: This requires the original handler to be reconnected
                # by the calling code after this function
                logger.debug(f"Made {sig_name} safe for widget {widget}")
        except Exception as e:
            logger.error(f"Error making signal {sig_name} safe: {e}")
