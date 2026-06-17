"""Helper functions for sales view safety checks"""
from pos_app.utils.sales_logger import sales_logger

def safe_calculate_change(widget, total):
    """Safely calculate and display change with proper error handling"""
    try:
        if not hasattr(widget, 'amount_paid_input') or not widget.amount_paid_input:
            sales_logger.log_error('change_calculation', 'Missing amount_paid_input')
            return
            
        paid = float(widget.amount_paid_input.value())
        change = max(0.0, paid - total)
        
        if hasattr(widget, 'change_label') and widget.change_label:
            widget.change_label.setText(f"Change to Give: Rs {change:,.2f}")
        elif hasattr(widget, 'calculate_change'):
            widget.calculate_change()
            
    except Exception as e:
        sales_logger.log_error('change_calculation', e, f"Total: {total}")
