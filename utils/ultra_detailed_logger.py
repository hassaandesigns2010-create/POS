"""
Ultra Detailed Logging System for POS Application
Tracks every user interaction and stock operation with extreme detail
"""

import logging
import json
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, List
from functools import wraps
import inspect
import os

class UltraDetailedLogger:
    """Ultra-detailed logging system for POS operations"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.setup_loggers()
        
    def setup_loggers(self):
        """Setup multiple specialized loggers"""
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Stock Operations Logger
        self.stock_logger = logging.getLogger('stock_operations')
        self.stock_logger.setLevel(logging.DEBUG)
        stock_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_stock.log'),
            encoding='utf-8'
        )
        stock_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )
        stock_handler.setFormatter(stock_formatter)
        self.stock_logger.addHandler(stock_handler)
        self.stock_logger.propagate = False
        
        # User Interactions Logger
        self.user_logger = logging.getLogger('user_interactions')
        self.user_logger.setLevel(logging.DEBUG)
        user_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_user.log'),
            encoding='utf-8'
        )
        user_handler.setFormatter(stock_formatter)
        self.user_logger.addHandler(user_handler)
        self.user_logger.propagate = False
        
        # Click Events Logger
        self.click_logger = logging.getLogger('click_events')
        self.click_logger.setLevel(logging.DEBUG)
        click_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_clicks.log'),
            encoding='utf-8'
        )
        click_handler.setFormatter(stock_formatter)
        self.click_logger.addHandler(click_handler)
        self.click_logger.propagate = False
        
        # Data Changes Logger
        self.data_logger = logging.getLogger('data_changes')
        self.data_logger.setLevel(logging.DEBUG)
        data_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_data.log'),
            encoding='utf-8'
        )
        data_handler.setFormatter(stock_formatter)
        self.data_logger.addHandler(data_handler)
        self.data_logger.propagate = False
        
        # Performance Logger
        self.perf_logger = logging.getLogger('performance')
        self.perf_logger.setLevel(logging.DEBUG)
        perf_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_performance.log'),
            encoding='utf-8'
        )
        perf_handler.setFormatter(stock_formatter)
        self.perf_logger.addHandler(perf_handler)
        self.perf_logger.propagate = False
        
        # Error Logger
        self.error_logger = logging.getLogger('detailed_errors')
        self.error_logger.setLevel(logging.DEBUG)
        error_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'ultra_detailed_errors.log'),
            encoding='utf-8'
        )
        error_handler.setFormatter(stock_formatter)
        self.error_logger.addHandler(error_handler)
        self.error_logger.propagate = False
    
    def log_stock_operation(self, operation: str, product_id: int, product_name: str, 
                          old_stock: float, new_stock: float, quantity: float, 
                          user: str, reason: str, **kwargs):
        """Log stock operation with extreme detail"""
        timestamp = datetime.now().isoformat()
        
        stock_data = {
            'timestamp': timestamp,
            'operation': operation,
            'product_id': product_id,
            'product_name': product_name,
            'old_stock': float(old_stock),
            'new_stock': float(new_stock),
            'quantity_change': float(quantity),
            'user': user,
            'reason': reason,
            'stock_difference': float(new_stock - old_stock),
            'percentage_change': self._calculate_percentage_change(old_stock, new_stock),
            'session_id': kwargs.get('session_id', 'N/A'),
            'ip_address': kwargs.get('ip_address', 'N/A'),
            'computer_name': kwargs.get('computer_name', 'N/A'),
            'additional_data': kwargs
        }
        
        self.stock_logger.info(f"STOCK_OPERATION: {json.dumps(stock_data, indent=2, default=str)}")
        
        # Log critical stock changes
        if new_stock <= 0:
            self.stock_logger.critical(f"CRITICAL_STOCK_EMPTY: {product_name} (ID: {product_id}) is now EMPTY")
        elif new_stock <= 5:
            self.stock_logger.warning(f"LOW_STOCK_WARNING: {product_name} (ID: {product_id}) has only {new_stock} units left")
    
    def log_user_click(self, widget_name: str, widget_type: str, action: str, 
                      user: str, **kwargs):
        """Log user click with extreme detail"""
        timestamp = datetime.now().isoformat()
        
        click_data = {
            'timestamp': timestamp,
            'widget_name': widget_name,
            'widget_type': widget_type,
            'action': action,
            'user': user,
            'mouse_position': kwargs.get('mouse_position', 'N/A'),
            'keyboard_modifiers': kwargs.get('keyboard_modifiers', 'N/A'),
            'screen_resolution': kwargs.get('screen_resolution', 'N/A'),
            'application_state': kwargs.get('application_state', 'N/A'),
            'current_page': kwargs.get('current_page', 'N/A'),
            'session_duration': kwargs.get('session_duration', 'N/A'),
            'click_count': kwargs.get('click_count', 1),
            'time_since_last_click': kwargs.get('time_since_last_click', 'N/A'),
            'additional_data': kwargs
        }
        
        self.click_logger.info(f"USER_CLICK: {json.dumps(click_data, indent=2, default=str)}")
    
    def log_user_interaction(self, interaction_type: str, component: str, 
                           action: str, user: str, **kwargs):
        """Log any user interaction with extreme detail"""
        timestamp = datetime.now().isoformat()
        
        interaction_data = {
            'timestamp': timestamp,
            'interaction_type': interaction_type,
            'component': component,
            'action': action,
            'user': user,
            'duration': kwargs.get('duration', 'N/A'),
            'input_data': kwargs.get('input_data', 'N/A'),
            'result': kwargs.get('result', 'N/A'),
            'error': kwargs.get('error', 'N/A'),
            'stack_trace': kwargs.get('stack_trace', 'N/A'),
            'memory_usage': kwargs.get('memory_usage', 'N/A'),
            'cpu_usage': kwargs.get('cpu_usage', 'N/A'),
            'network_status': kwargs.get('network_status', 'N/A'),
            'database_status': kwargs.get('database_status', 'N/A'),
            'additional_data': kwargs
        }
        
        self.user_logger.info(f"USER_INTERACTION: {json.dumps(interaction_data, indent=2, default=str)}")
    
    def log_data_change(self, table_name: str, operation: str, record_id: int, 
                       old_data: Dict, new_data: Dict, user: str, **kwargs):
        """Log data changes with extreme detail"""
        timestamp = datetime.now().isoformat()
        
        # Calculate field changes
        field_changes = {}
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                field_changes[key] = {
                    'old_value': old_value,
                    'new_value': new_value,
                    'change_type': self._get_change_type(old_value, new_value)
                }
        
        change_data = {
            'timestamp': timestamp,
            'table_name': table_name,
            'operation': operation,
            'record_id': record_id,
            'user': user,
            'field_changes': field_changes,
            'total_fields_changed': len(field_changes),
            'primary_keys': kwargs.get('primary_keys', {}),
            'foreign_keys': kwargs.get('foreign_keys', {}),
            'transaction_id': kwargs.get('transaction_id', 'N/A'),
            'rollback_info': kwargs.get('rollback_info', 'N/A'),
            'validation_results': kwargs.get('validation_results', 'N/A'),
            'additional_data': kwargs
        }
        
        self.data_logger.info(f"DATA_CHANGE: {json.dumps(change_data, indent=2, default=str)}")
        
        # Log critical data changes
        if table_name in ['products', 'sales', 'customers'] and operation in ['DELETE', 'UPDATE']:
            self.data_logger.warning(f"CRITICAL_DATA_CHANGE: {operation} on {table_name} ID {record_id} by {user}")
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        timestamp = datetime.now().isoformat()
        
        perf_data = {
            'timestamp': timestamp,
            'operation': operation,
            'duration_ms': duration * 1000,
            'duration_seconds': duration,
            'performance_tier': self._get_performance_tier(duration),
            'memory_before': kwargs.get('memory_before', 'N/A'),
            'memory_after': kwargs.get('memory_after', 'N/A'),
            'memory_peak': kwargs.get('memory_peak', 'N/A'),
            'cpu_usage': kwargs.get('cpu_usage', 'N/A'),
            'database_queries': kwargs.get('database_queries', 'N/A'),
            'cache_hits': kwargs.get('cache_hits', 'N/A'),
            'cache_misses': kwargs.get('cache_misses', 'N/A'),
            'network_requests': kwargs.get('network_requests', 'N/A'),
            'thread_count': kwargs.get('thread_count', 'N/A'),
            'additional_data': kwargs
        }
        
        self.perf_logger.info(f"PERFORMANCE: {json.dumps(perf_data, indent=2, default=str)}")
        
        # Log performance warnings
        if duration > 5.0:
            self.perf_logger.warning(f"SLOW_OPERATION: {operation} took {duration:.2f}s")
        elif duration > 1.0:
            self.perf_logger.warning(f"MODERATE_OPERATION: {operation} took {duration:.2f}s")
    
    def log_error(self, error: Exception, context: str, user: str, **kwargs):
        """Log errors with extreme detail"""
        timestamp = datetime.now().isoformat()
        
        error_data = {
            'timestamp': timestamp,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user': user,
            'stack_trace': traceback.format_exc(),
            'function_name': kwargs.get('function_name', 'N/A'),
            'line_number': kwargs.get('line_number', 'N/A'),
            'file_name': kwargs.get('file_name', 'N/A'),
            'module_name': kwargs.get('module_name', 'N/A'),
            'class_name': kwargs.get('class_name', 'N/A'),
            'method_name': kwargs.get('method_name', 'N/A'),
            'arguments': kwargs.get('arguments', 'N/A'),
            'local_variables': kwargs.get('local_variables', 'N/A'),
            'global_variables': kwargs.get('global_variables', 'N/A'),
            'system_state': kwargs.get('system_state', 'N/A'),
            'user_session': kwargs.get('user_session', 'N/A'),
            'additional_data': kwargs
        }
        
        self.error_logger.error(f"ERROR: {json.dumps(error_data, indent=2, default=str)}")
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / old_value) * 100
    
    def _get_change_type(self, old_value: Any, new_value: Any) -> str:
        """Determine the type of change"""
        if old_value is None and new_value is not None:
            return 'CREATED'
        elif old_value is not None and new_value is None:
            return 'DELETED'
        elif old_value != new_value:
            return 'MODIFIED'
        else:
            return 'UNCHANGED'
    
    def _get_performance_tier(self, duration: float) -> str:
        """Categorize performance tier"""
        if duration < 0.1:
            return 'EXCELLENT'
        elif duration < 0.5:
            return 'GOOD'
        elif duration < 1.0:
            return 'ACCEPTABLE'
        elif duration < 2.0:
            return 'SLOW'
        else:
            return 'VERY_SLOW'

# Global instance
ultra_logger = UltraDetailedLogger()

def log_detailed(operation_type: str, include_args: bool = True, include_result: bool = True):
    """Decorator for ultra-detailed function logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            module_name = func.__module__
            
            # Get calling frame info
            frame = inspect.currentframe()
            caller_frame = frame.f_back.f_back if frame else None
            
            # Prepare logging data
            log_data = {
                'function_name': func_name,
                'module_name': module_name,
                'operation_type': operation_type,
                'start_time': datetime.now().isoformat(),
                'args_count': len(args) if include_args else 'N/A',
                'kwargs_count': len(kwargs) if include_args else 'N/A',
                'caller_file': caller_frame.f_code.co_filename if caller_frame else 'N/A',
                'caller_line': caller_frame.f_lineno if caller_frame else 'N/A',
                'caller_function': caller_frame.f_code.co_name if caller_frame else 'N/A'
            }
            
            if include_args:
                log_data['arguments'] = str(args) if args else 'None'
                log_data['keyword_arguments'] = str(kwargs) if kwargs else 'None'
            
            try:
                # Log function start
                ultra_logger.log_user_interaction(
                    interaction_type='FUNCTION_START',
                    component=func_name,
                    action='EXECUTION_STARTED',
                    user=kwargs.get('user', 'SYSTEM'),
                    **log_data
                )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Log successful completion
                completion_data = log_data.copy()
                completion_data['end_time'] = datetime.now().isoformat()
                completion_data['duration'] = duration
                completion_data['success'] = True
                
                if include_result:
                    completion_data['result'] = str(result) if result is not None else 'None'
                    completion_data['result_type'] = type(result).__name__ if result is not None else 'None'
                
                ultra_logger.log_user_interaction(
                    interaction_type='FUNCTION_COMPLETE',
                    component=func_name,
                    action='EXECUTION_SUCCESS',
                    user=kwargs.get('user', 'SYSTEM'),
                    **completion_data
                )
                
                # Log performance
                ultra_logger.log_performance(
                    operation=f"{module_name}.{func_name}",
                    duration=duration,
                    **log_data
                )
                
                return result
                
            except Exception as e:
                # Calculate duration even for errors
                duration = time.time() - start_time
                
                # Log error
                error_data = log_data.copy()
                error_data['end_time'] = datetime.now().isoformat()
                error_data['duration'] = duration
                error_data['success'] = False
                error_data['error'] = str(e)
                error_data['error_type'] = type(e).__name__
                
                ultra_logger.log_error(
                    error=e,
                    context=f"Function execution failed: {func_name}",
                    user=kwargs.get('user', 'SYSTEM'),
                    **error_data
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator

# Convenience functions for common logging tasks
def log_stock_change(operation: str, product_id: int, product_name: str, 
                    old_stock: float, new_stock: float, quantity: float, 
                    user: str, reason: str, **kwargs):
    """Convenience function for stock logging"""
    ultra_logger.log_stock_operation(
        operation, product_id, product_name, old_stock, new_stock, 
        quantity, user, reason, **kwargs
    )

def log_click(widget_name: str, widget_type: str, action: str, user: str, **kwargs):
    """Convenience function for click logging"""
    ultra_logger.log_user_click(widget_name, widget_type, action, user, **kwargs)

def log_interaction(interaction_type: str, component: str, action: str, user: str, **kwargs):
    """Convenience function for interaction logging"""
    ultra_logger.log_user_interaction(interaction_type, component, action, user, **kwargs)

def log_data_change(table_name: str, operation: str, record_id: int, 
                   old_data: Dict, new_data: Dict, user: str, **kwargs):
    """Convenience function for data change logging"""
    ultra_logger.log_data_change(table_name, operation, record_id, old_data, new_data, user, **kwargs)
