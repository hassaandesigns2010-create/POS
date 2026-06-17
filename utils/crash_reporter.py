"""Centralized crash reporting system"""
import traceback
from datetime import datetime
from pathlib import Path

class CrashReporter:
    def __init__(self, log_dir="logs"):
        self.log_file = Path(log_dir) / "crashes.log"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_crash(self, location, exception, context=None):
        """Log crash details with context"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trace = ''.join(traceback.format_tb(exception.__traceback__))
        
        with open(self.log_file, 'a') as f:
            f.write(f"\n=== CRASH @ {timestamp} ===\n")
            f.write(f"Location: {location}\n")
            f.write(f"Type: {type(exception).__name__}\n")
            f.write(f"Message: {str(exception)}\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(f"Traceback:\n{trace}\n")

# Global instance
crash_reporter = CrashReporter()
