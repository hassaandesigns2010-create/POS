"""Utilities for safe controller access"""
from pos_app.utils.crash_reporter import crash_reporter

def safe_controller_call(controller, method, *args, **kwargs):
    """Safely call controller method with null checks"""
    if not controller:
        crash_reporter.log_crash(
            'controller_access',
            Exception('Null controller'),
            {'method': method}
        )
        raise ValueError("Controller not available")
    
    try:
        return getattr(controller, method)(*args, **kwargs)
    except Exception as e:
        crash_reporter.log_crash(
            'controller_method',
            e,
            {'method': method, 'args': args, 'kwargs': kwargs}
        )
        raise
