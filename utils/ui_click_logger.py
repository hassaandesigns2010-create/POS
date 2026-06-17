"""
UI Click Logger for Ultra-Detailed User Interaction Tracking
Captures every click, keypress, and user interaction with extreme detail
"""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import inspect
import os
import psutil
import platform

from pos_app.utils.ultra_detailed_logger import ultra_logger

class UIClickLogger:
    """Ultra-detailed UI interaction logger"""
    
    def __init__(self):
        self.click_count = 0
        self.last_click_time = None
        self.session_start_time = datetime.now()
        self.current_user = 'UNKNOWN'
        
    def set_current_user(self, username: str):
        """Set the current user for logging"""
        self.current_user = username
        ultra_logger.log_interaction(
            interaction_type='USER_SESSION_START',
            component='UI',
            action='USER_LOGIN',
            user=username,
            session_start=self.session_start_time.isoformat()
        )
    
    def log_click(self, widget, event=None, **kwargs):
        """Log a widget click with extreme detail"""
        self.click_count += 1
        current_time = datetime.now()
        
        # Calculate time since last click
        time_since_last_click = None
        if self.last_click_time:
            time_since_last_click = (current_time - self.last_click_time).total_seconds()
        self.last_click_time = current_time
        
        # Get widget information
        widget_name = getattr(widget, 'objectName', '') or widget.__class__.__name__
        widget_type = widget.__class__.__name__
        widget_text = getattr(widget, 'text', lambda: '')() if hasattr(widget, 'text') else ''
        widget_tooltip = getattr(widget, 'toolTip', lambda: '')() if hasattr(widget, 'toolTip') else ''
        
        # Get mouse position if available
        mouse_pos = 'N/A'
        if event and hasattr(event, 'pos'):
            mouse_pos = f"{event.pos().x()},{event.pos().y()}"
        elif event and hasattr(event, 'globalPos'):
            mouse_pos = f"{event.globalPos().x()},{event.globalPos().y()}"
        
        # Get keyboard modifiers
        keyboard_modifiers = 'N/A'
        if event and hasattr(event, 'modifiers'):
            modifiers = event.modifiers()
            modifier_list = []
            if modifiers & 0x02000000:  # Ctrl
                modifier_list.append('Ctrl')
            if modifiers & 0x04000000:  # Alt
                modifier_list.append('Alt')
            if modifiers & 0x08000000:  # Shift
                modifier_list.append('Shift')
            keyboard_modifiers = '+'.join(modifier_list) if modifier_list else 'None'
        
        # Get system information
        try:
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
        except:
            memory_info = None
            cpu_percent = 'N/A'
        
        # Get screen resolution
        try:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            screen_size = f"{screen.size().width()}x{screen.size().height()}"
        except:
            try:
                from PyQt6.QtWidgets import QApplication
                screen = QApplication.primaryScreen()
                screen_size = f"{screen.size().width()}x{screen.size().height()}"
            except:
                screen_size = 'N/A'
        
        # Get current application state
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            current_widget = app.focusWidget() if app else None
            current_page = current_widget.objectName() if current_widget else 'N/A'
        except:
            try:
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
                current_widget = app.focusWidget() if app else None
                current_page = current_widget.objectName() if current_widget else 'N/A'
            except:
                current_page = 'N/A'
        
        # Calculate session duration
        session_duration = (current_time - self.session_start_time).total_seconds()
        
        # Prepare click data
        click_data = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'widget_text': widget_text,
            'widget_tooltip': widget_tooltip,
            'widget_properties': self._get_widget_properties(widget),
            'mouse_position': mouse_pos,
            'keyboard_modifiers': keyboard_modifiers,
            'screen_resolution': screen_size,
            'current_page': current_page,
            'click_count': self.click_count,
            'time_since_last_click': time_since_last_click,
            'session_duration': session_duration,
            'system_info': {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'memory_usage': {
                    'total': memory_info.total if memory_info else 'N/A',
                    'available': memory_info.available if memory_info else 'N/A',
                    'percent': memory_info.percent if memory_info else 'N/A'
                },
                'cpu_percent': cpu_percent
            },
            'timestamp': current_time.isoformat(),
            'additional_data': kwargs
        }
        
        # Log the click
        ultra_logger.log_click(
            widget_name=widget_name,
            widget_type=widget_type,
            action='CLICK',
            user=self.current_user,
            **click_data
        )
        
        # Log special interactions
        self._log_special_interactions(widget, click_data)
    
    def log_keypress(self, widget, key_event, **kwargs):
        """Log keypress with extreme detail"""
        current_time = datetime.now()
        
        # Get key information
        key_text = key_event.text() if hasattr(key_event, 'text') else ''
        key_code = key_event.key() if hasattr(key_event, 'key') else 'N/A'
        key_name = self._get_key_name(key_code) if key_code != 'N/A' else 'N/A'
        
        # Get widget information
        widget_name = getattr(widget, 'objectName', '') or widget.__class__.__name__
        widget_type = widget.__class__.__name__
        
        # Get modifier keys
        modifiers = []
        if hasattr(key_event, 'modifiers'):
            mod = key_event.modifiers()
            if mod & 0x02000000:  # Ctrl
                modifiers.append('Ctrl')
            if mod & 0x04000000:  # Alt
                modifiers.append('Alt')
            if mod & 0x08000000:  # Shift
                modifiers.append('Shift')
        
        keypress_data = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'key_text': key_text,
            'key_code': key_code,
            'key_name': key_name,
            'modifiers': modifiers,
            'is_auto_repeat': getattr(key_event, 'isAutoRepeat', False),
            'timestamp': current_time.isoformat(),
            'additional_data': kwargs
        }
        
        ultra_logger.log_interaction(
            interaction_type='KEYPRESS',
            component=widget_name,
            action=f'KEY_{key_name}',
            user=self.current_user,
            **keypress_data
        )
    
    def log_form_submit(self, form_data: Dict[str, Any], form_name: str, **kwargs):
        """Log form submission with extreme detail"""
        current_time = datetime.now()
        
        # Sanitize form data for logging
        sanitized_data = {}
        for key, value in form_data.items():
            if 'password' in key.lower() or 'pin' in key.lower() or 'secret' in key.lower():
                sanitized_data[key] = '[REDACTED]'
            else:
                sanitized_data[key] = str(value) if value is not None else 'None'
        
        form_data_log = {
            'form_name': form_name,
            'form_data': sanitized_data,
            'field_count': len(form_data),
            'timestamp': current_time.isoformat(),
            'additional_data': kwargs
        }
        
        ultra_logger.log_interaction(
            interaction_type='FORM_SUBMIT',
            component=form_name,
            action='SUBMIT',
            user=self.current_user,
            **form_data_log
        )
    
    def log_navigation(self, from_page: str, to_page: str, **kwargs):
        """Log page navigation"""
        current_time = datetime.now()
        
        nav_data = {
            'from_page': from_page,
            'to_page': to_page,
            'timestamp': current_time.isoformat(),
            'session_duration': (current_time - self.session_start_time).total_seconds(),
            'additional_data': kwargs
        }
        
        ultra_logger.log_interaction(
            interaction_type='NAVIGATION',
            component='MAIN_WINDOW',
            action=f'NAVIGATE_{from_page}_TO_{to_page}',
            user=self.current_user,
            **nav_data
        )
    
    def log_error_dialog(self, error_message: str, dialog_type: str, **kwargs):
        """Log error dialog appearance"""
        current_time = datetime.now()
        
        error_data = {
            'error_message': error_message,
            'dialog_type': dialog_type,
            'timestamp': current_time.isoformat(),
            'session_duration': (current_time - self.session_start_time).total_seconds(),
            'additional_data': kwargs
        }
        
        ultra_logger.log_interaction(
            interaction_type='ERROR_DIALOG',
            component=dialog_type,
            action='ERROR_SHOWN',
            user=self.current_user,
            **error_data
        )
    
    def _get_widget_properties(self, widget) -> Dict[str, Any]:
        """Get relevant widget properties for logging"""
        properties = {}
        
        # Common properties
        if hasattr(widget, 'isEnabled'):
            properties['enabled'] = widget.isEnabled()
        if hasattr(widget, 'isVisible'):
            properties['visible'] = widget.isVisible()
        if hasattr(widget, 'width'):
            properties['width'] = widget.width()
        if hasattr(widget, 'height'):
            properties['height'] = widget.height()
        
        # Specific widget types
        if widget.__class__.__name__ == 'QLineEdit':
            if hasattr(widget, 'text'):
                text = widget.text()
                properties['text_length'] = len(text)
                properties['is_empty'] = len(text) == 0
                properties['is_numeric'] = text.isdigit() if text else False
        elif widget.__class__.__name__ == 'QComboBox':
            if hasattr(widget, 'currentIndex'):
                properties['current_index'] = widget.currentIndex()
            if hasattr(widget, 'count'):
                properties['item_count'] = widget.count()
        elif widget.__class__.__name__ == 'QSpinBox' or widget.__class__.__name__ == 'QDoubleSpinBox':
            if hasattr(widget, 'value'):
                properties['value'] = widget.value()
            if hasattr(widget, 'minimum'):
                properties['minimum'] = widget.minimum()
            if hasattr(widget, 'maximum'):
                properties['maximum'] = widget.maximum()
        elif widget.__class__.__name__ == 'QTableWidget':
            if hasattr(widget, 'rowCount'):
                properties['row_count'] = widget.rowCount()
            if hasattr(widget, 'columnCount'):
                properties['column_count'] = widget.columnCount()
            if hasattr(widget, 'currentRow'):
                properties['current_row'] = widget.currentRow()
        
        return properties
    
    def _get_key_name(self, key_code: int) -> str:
        """Get key name from key code"""
        key_names = {
            32: 'Space',
            13: 'Enter',
            8: 'Backspace',
            9: 'Tab',
            16777216: 'Esc',
            16777248: 'F1',
            16777249: 'F2',
            16777250: 'F3',
            16777251: 'F4',
            16777252: 'F5',
            16777253: 'F6',
            16777254: 'F7',
            16777255: 'F8',
            16777256: 'F9',
            16777257: 'F10',
            16777258: 'F11',
            16777259: 'F12',
            16777220: 'Delete',
            16777219: 'Home',
            16777222: 'End',
            16777223: 'PageUp',
            16777224: 'PageDown',
        }
        return key_names.get(key_code, f'Key_{key_code}')
    
    def _log_special_interactions(self, widget, click_data: Dict[str, Any]):
        """Log special interactions based on widget type and properties"""
        widget_name = click_data['widget_name']
        widget_type = click_data['widget_type']
        
        # Log button clicks with special attention
        if 'Button' in widget_type:
            if 'DELETE' in widget_name.upper() or 'REMOVE' in widget_name.upper():
                ultra_logger.log_interaction(
                    interaction_type='CRITICAL_BUTTON_CLICK',
                    component=widget_name,
                    action='DELETE_ACTION',
                    user=self.current_user,
                    **click_data
                )
            elif 'SAVE' in widget_name.upper() or 'SUBMIT' in widget_name.upper():
                ultra_logger.log_interaction(
                    interaction_type='SAVE_BUTTON_CLICK',
                    component=widget_name,
                    action='SAVE_ACTION',
                    user=self.current_user,
                    **click_data
                )
        
        # Log table interactions
        if 'Table' in widget_type:
            ultra_logger.log_interaction(
                interaction_type='TABLE_INTERACTION',
                component=widget_name,
                action='TABLE_CLICK',
                user=self.current_user,
                **click_data
            )
        
        # Log input field interactions
        if 'LineEdit' in widget_type or 'SpinBox' in widget_type:
            ultra_logger.log_interaction(
                interaction_type='INPUT_FIELD_INTERACTION',
                component=widget_name,
                action='INPUT_CLICK',
                user=self.current_user,
                **click_data
            )

# Global instance
ui_click_logger = UIClickLogger()

# Decorator for automatic UI logging
def log_ui_clicks(func):
    """Decorator to automatically log UI interactions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to extract widget from arguments
        widget = None
        for arg in args:
            if hasattr(arg, '__class__') and 'Widget' in arg.__class__.__name__:
                widget = arg
                break
        
        if widget:
            ui_click_logger.log_click(widget, **kwargs)
        
        return func(*args, **kwargs)
    return wrapper

# Convenience functions
def set_current_user(username: str):
    """Set the current user for UI logging"""
    ui_click_logger.set_current_user(username)

def log_widget_click(widget, event=None, **kwargs):
    """Log a widget click"""
    ui_click_logger.log_click(widget, event, **kwargs)

def log_keypress(widget, key_event, **kwargs):
    """Log a keypress"""
    ui_click_logger.log_keypress(widget, key_event, **kwargs)

def log_form_submit(form_data: Dict[str, Any], form_name: str, **kwargs):
    """Log form submission"""
    ui_click_logger.log_form_submit(form_data, form_name, **kwargs)

def log_navigation(from_page: str, to_page: str, **kwargs):
    """Log page navigation"""
    ui_click_logger.log_navigation(from_page, to_page, **kwargs)

def log_error_dialog(error_message: str, dialog_type: str, **kwargs):
    """Log error dialog"""
    ui_click_logger.log_error_dialog(error_message, dialog_type, **kwargs)
