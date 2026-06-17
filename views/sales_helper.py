"""Helper functions for safe sales operations"""
from pos_app.utils.controller_utils import safe_controller_call

def safe_process_sale(widget):
    """Safely process sale with null checks"""
    if not hasattr(widget, 'controller') or not widget.controller:
        raise ValueError("SalesWidget missing controller")
    
    return safe_controller_call(
        widget.controller,
        'create_sale',
        widget.customer_combo.currentData() if hasattr(widget, 'customer_combo') else None,
        widget.current_cart,
        # Include other required args
    )
