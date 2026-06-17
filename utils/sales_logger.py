"""Detailed logging for sales process"""
from pos_app.utils.logger import setup_logger

class SalesLogger:
    def __init__(self):
        self.logger = setup_logger('sales_process')
    
    def log_step(self, step_name, details=None):
        """Log a step in the sales process"""
        msg = f"Sales Step: {step_name}"
        if details:
            msg += f" | Details: {details}"
        self.logger.info(msg)
    
    def log_error(self, step_name, error, context=None):
        """Log a sales process error"""
        msg = f"Sales Error in {step_name}: {str(error)}"
        if context:
            msg += f" | Context: {context}"
        self.logger.error(msg, exc_info=True)

# Global instance for easy access
sales_logger = SalesLogger()
