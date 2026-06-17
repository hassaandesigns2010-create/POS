"""
Connection Monitor - Monitors database connection and auto-reloads data when server restarts
"""

import time
import threading
import logging
from typing import Callable, Dict, Any
from datetime import datetime

try:
    from PySide6.QtCore import QObject, Signal, QTimer
except ImportError:
    from PyQt6.QtCore import QObject, pyqtSignal as Signal, QTimer

logger = logging.getLogger('ConnectionMonitor')

class ConnectionMonitor(QObject):
    """Monitors database connection and triggers data reload when server restarts"""
    
    # Signal emitted when connection is restored
    connection_restored = Signal()
    # Signal emitted when connection is lost
    connection_lost = Signal()
    # Signal to reload specific data
    reload_data = Signal(str)  # str = data_type (products, customers, suppliers, etc.)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = True
        self.last_check_time = time.time()
        self.check_interval = 15000  # 15 seconds (increased from 5 to reduce load)
        self.consecutive_failures = 0
        self.max_failures = 3
        self.reload_callbacks: Dict[str, Callable] = {}
        self._controller = None
        
        # Setup timer for periodic connection checks
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_connection)
        
        logger.debug("Connection monitor initialized")

    def start_monitoring(self):
        """Start periodic connection checks explicitly."""
        if not self.timer.isActive():
            self.timer.start(self.check_interval)
            logger.debug("Connection monitor started")
    
    def set_controller(self, controller):
        """Set controller reference for database access"""
        self._controller = controller
        logger.debug("Controller reference set for connection monitor")
    
    def add_reload_callback(self, data_type: str, callback: Callable):
        """Add a callback to reload specific data type"""
        self.reload_callbacks[data_type] = callback
        logger.debug(f"Added reload callback for {data_type}")
    
    def check_connection(self):
        """Check database connection and handle connection changes"""
        try:
            # Try multiple ways to get database session
            from sqlalchemy import text
            session = None
            result = None
            
            # Method 1: Try canonical context-managed session helper
            try:
                from pos_app.database.db_utils import get_db_session
                with get_db_session() as session:
                    result = session.execute(text("SELECT 1")).scalar()
            except (ImportError, AttributeError, TypeError):
                # Method 2: Try direct Database class
                try:
                    from pos_app.database.connection import Database
                    db = Database()
                    session = db.session
                    result = session.execute(text("SELECT 1")).scalar()
                except (ImportError, AttributeError):
                    # Method 3: Try controller session if available
                    try:
                        # Check if we have access to controller
                        if hasattr(self, '_controller') and self._controller:
                            session = self._controller.session
                            result = session.execute(text("SELECT 1")).scalar()
                        else:
                            raise ImportError("No controller available")
                    except (ImportError, AttributeError):
                        # Method 4: Simple ping test without database
                        import time as time_module
                        if self.is_connected:
                            # Just check if enough time has passed since last check
                            if time_module.time() - self.last_check_time < 30:
                                # Assume still connected if recent check was good
                                return
                        raise ImportError("All connection methods failed")
            
            if result == 1:
                # Connection is working
                if not self.is_connected:
                    # Connection was just restored
                    self.is_connected = True
                    self.consecutive_failures = 0
                    logger.info("Database connection restored")
                    
                    # Emit signal
                    self.connection_restored.emit()
                    
                    # Trigger data reload for all registered callbacks
                    self.trigger_data_reload()
                
                self.last_check_time = time.time()
            else:
                raise Exception("Invalid query result")
                
        except Exception as e:
            self.consecutive_failures += 1
            logger.warning(f"Connection check failed (attempt {self.consecutive_failures}): {e}")
            
            if self.is_connected and self.consecutive_failures >= self.max_failures:
                # Connection lost
                self.is_connected = False
                logger.error("Database connection lost")
                self.connection_lost.emit()
            
            # Prevent excessive logging
            if self.consecutive_failures % 10 == 0:  # Log every 10th failure
                logger.error(f"Connection check failing repeatedly: {self.consecutive_failures} attempts")
    
    def trigger_data_reload(self):
        """Trigger data reload for all registered callbacks"""
        logger.debug("Triggering data reload for all components")
        
        for data_type, callback in self.reload_callbacks.items():
            try:
                logger.debug(f"Reloading {data_type}")
                # Emit signal for UI components
                self.reload_data.emit(data_type)
                # Also call direct callback if provided
                if callback:
                    callback()
            except Exception as e:
                logger.error(f"Failed to reload {data_type}: {e}")
    
    def force_reload(self, data_type: str = None):
        """Force reload of specific data type or all data"""
        if data_type:
            logger.debug(f"Force reloading {data_type}")
            self.reload_data.emit(data_type)
            if data_type in self.reload_callbacks:
                self.reload_callbacks[data_type]()
        else:
            self.trigger_data_reload()
    
    def stop_monitoring(self):
        """Stop the connection monitoring timer"""
        if self.timer.isActive():
            self.timer.stop()
            logger.debug("Connection monitor stopped")


# Global instance
_connection_monitor = None

def get_connection_monitor() -> ConnectionMonitor:
    """Get or create global connection monitor instance"""
    global _connection_monitor
    if _connection_monitor is None:
        _connection_monitor = ConnectionMonitor()
    return _connection_monitor

def initialize_connection_monitor(app_instance):
    """Initialize connection monitor within Qt application"""
    monitor = get_connection_monitor()
    monitor.start_monitoring()
    
    # Store reference to prevent garbage collection
    app_instance._connection_monitor = monitor
    
    logger.debug("Connection monitor initialized in application")
    return monitor
