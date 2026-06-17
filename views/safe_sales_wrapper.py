"""Safe wrapper for SalesWidget with comprehensive error handling"""
from pos_app.utils.crash_reporter import crash_reporter
from pos_app.utils.sales_fixes import SalesFixes
from pos_app.views.sales import SalesWidget
from pos_app.views.sales_helper import safe_process_sale

class SafeSalesWrapper(SalesWidget):
    """SalesWidget with enhanced safety features"""
    
    def process_sale(self):
        """Override process_sale with safe implementation"""
        try:
            # Verify controller exists
            if not hasattr(self, 'controller') or not self.controller:
                raise ValueError("Missing controller")
                
            # Process sale safely
            return safe_process_sale(self)
            
        except Exception as e:
            crash_reporter.log_crash('process_sale', e, {
                'has_controller': hasattr(self, 'controller'),
                'cart_items': len(getattr(self, 'current_cart', []))
            })
            raise

    def _update_totals(self):
        """Override with safe totals update"""
        try:
            SalesFixes.safe_update_totals(self)
        except Exception as e:
            crash_reporter.log_crash('update_totals', e, {
                'method': '_update_totals',
                'state': {
                    'has_amount_input': hasattr(self, 'amount_paid_input'),
                    'has_change_label': hasattr(self, 'change_label')
                }
            })
            raise
