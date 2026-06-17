"""Wrapper for SalesWidget with crash reporting"""
from pos_app.utils.crash_decorator import report_crashes
from pos_app.views.sales import SalesWidget

class SafeSalesWidget(SalesWidget):
    """SalesWidget with automatic crash reporting"""
    
    @report_crashes
    def process_sale(self):
        return super().process_sale()
    
    @report_crashes
    def _calculate_totals(self):
        return super()._calculate_totals()
    
    @report_crashes
    def update_cart_table(self):
        return super().update_cart_table()
