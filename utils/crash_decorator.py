"""Decorator for automatic crash reporting"""
from functools import wraps
from pos_app.utils.crash_reporter import crash_reporter

def report_crashes(func):
    """Decorator to automatically log crashes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            crash_reporter.log_crash(
                location=f"{func.__module__}.{func.__name__}",
                exception=e,
                context=f"args={args}, kwargs={kwargs}"
            )
            raise
    return wrapper
