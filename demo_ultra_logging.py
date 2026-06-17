#!/usr/bin/env python3
"""
Ultra-Detailed Logging Demo
Shows the extreme logging capabilities in action
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.utils.ultra_detailed_logger import (
        ultra_logger, log_detailed, log_stock_change, log_data_change, log_interaction
    )
    from pos_app.utils.ui_click_logger import (
        ui_click_logger, set_current_user, log_widget_click, log_form_submit, 
        log_navigation, log_error_dialog
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in standalone mode...")
    
    # Create minimal logging for demo
    import logging
    import json
    
    class DemoLogger:
        def __init__(self):
            self.log_dir = "logs"
            os.makedirs(self.log_dir, exist_ok=True)
            self.setup_logger()
        
        def setup_logger(self):
            self.logger = logging.getLogger('demo_ultra')
            self.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(os.path.join(self.log_dir, 'demo_ultra_detailed.log'))
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        def log_stock_change(self, **kwargs):
            self.logger.info(f"STOCK_CHANGE: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_widget_click(self, **kwargs):
            self.logger.info(f"CLICK: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_form_submit(self, **kwargs):
            self.logger.info(f"FORM_SUBMIT: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_navigation(self, **kwargs):
            self.logger.info(f"NAVIGATION: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_error_dialog(self, **kwargs):
            self.logger.info(f"ERROR_DIALOG: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_interaction(self, **kwargs):
            self.logger.info(f"INTERACTION: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_data_change(self, **kwargs):
            self.logger.info(f"DATA_CHANGE: {json.dumps(kwargs, indent=2, default=str)}")
        
        def log_performance(self, **kwargs):
            self.logger.info(f"PERFORMANCE: {json.dumps(kwargs, indent=2, default=str)}")
    
    # Create demo instances
    ultra_logger = DemoLogger()
    ui_click_logger = DemoLogger()
    
    def log_stock_change(**kwargs):
        ultra_logger.log_stock_change(**kwargs)
    
    def log_widget_click(**kwargs):
        ultra_logger.log_widget_click(**kwargs)
    
    def log_form_submit(**kwargs):
        ultra_logger.log_form_submit(**kwargs)
    
    def log_navigation(**kwargs):
        ultra_logger.log_navigation(**kwargs)
    
    def log_error_dialog(**kwargs):
        ultra_logger.log_error_dialog(**kwargs)
    
    def log_interaction(**kwargs):
        ultra_logger.log_interaction(**kwargs)
    
    def log_data_change(**kwargs):
        ultra_logger.log_data_change(**kwargs)
    
    def set_current_user(username):
        print(f"Setting current user: {username}")
    
    def log_detailed(operation_type, include_args=True, include_result=True):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    ultra_logger.log_performance(
                        operation=f"{func.__module__}.{func.__name__}",
                        duration=duration,
                        operation_type=operation_type
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    ultra_logger.log_performance(
                        operation=f"{func.__module__}.{func.__name__}",
                        duration=duration,
                        operation_type=operation_type,
                        error=str(e)
                    )
                    raise
            return wrapper
        return decorator

def demo_stock_operations():
    """Demo ultra-detailed stock logging"""
    print("🔥 DEMO: Ultra-Detailed Stock Operations Logging")
    print("=" * 60)
    
    # Simulate stock decrease
    log_stock_change(
        operation='STOCK_SALE_DECREASE',
        product_id=1234,
        product_name='Test Product A',
        old_stock=50.0,
        new_stock=45.0,
        quantity=5.0,
        user='admin',
        reason='Sale #1234',
        sale_id=1234,
        unit_price=99.99,
        customer_id=567,
        payment_method='Cash',
        is_wholesale=False,
        barcode='1234567890123',
        category_id=1,
        supplier_id=10
    )
    
    # Simulate stock increase (purchase)
    log_stock_change(
        operation='STOCK_PURCHASE_INCREASE',
        product_id=1234,
        product_name='Test Product A',
        old_stock=45.0,
        new_stock=95.0,
        quantity=50.0,
        user='admin',
        reason='Purchase #789',
        purchase_id=789,
        unit_cost=45.50,
        supplier_id=10,
        invoice_number='PO-789',
        barcode='1234567890123'
    )
    
    # Simulate critical stock level
    log_stock_change(
        operation='STOCK_SALE_DECREASE',
        product_id=5678,
        product_name='Critical Stock Item',
        old_stock=3.0,
        new_stock=0.0,
        quantity=3.0,
        user='cashier',
        reason='Sale #1235',
        sale_id=1235,
        unit_price=199.99,
        customer_id=568,
        payment_method='Credit Card',
        is_wholesale=False,
        barcode='9876543210987'
    )
    
    print("✅ Stock operations logged with extreme detail!")

def demo_user_interactions():
    """Demo ultra-detailed user interaction logging"""
    print("\n🔥 DEMO: Ultra-Detailed User Interaction Logging")
    print("=" * 60)
    
    # Set current user
    set_current_user('admin_user')
    
    # Simulate button clicks
    log_widget_click(
        widget_name='add_product_button',
        widget_type='QPushButton',
        action='CLICK',
        user='admin_user',
        mouse_position='250,150',
        keyboard_modifiers='Ctrl',
        screen_resolution='1920x1080',
        current_page='SalesWidget',
        session_duration=3600.5,
        click_count=15,
        time_since_last_click=2.3,
        widget_text='Add Product',
        widget_tooltip='Click to add product to cart'
    )
    
    # Simulate form submission
    form_data = {
        'customer_name': 'John Doe',
        'phone': '123-456-7890',
        'email': 'john@example.com',
        'address': '123 Main St',
        'password': 'secret123'  # This will be redacted
    }
    
    log_form_submit(
        form_data=form_data,
        form_name='customer_registration',
        user='admin_user',
        form_validation_passed=True,
        processing_time_ms=150,
        database_write_time_ms=45
    )
    
    # Simulate navigation
    log_navigation(
        from_page='SalesWidget',
        to_page='InventoryWidget',
        user='admin_user',
        navigation_type='BUTTON_CLICK',
        transition_time_ms=200
    )
    
    # Simulate error dialog
    log_error_dialog(
        error_message='Insufficient stock for product "Test Product". Available: 5, Requested: 10',
        dialog_type='StockWarning',
        user='admin_user',
        error_code='STOCK_INSUFFICIENT',
        product_id=1234,
        product_name='Test Product'
    )
    
    print("✅ User interactions logged with extreme detail!")

def demo_function_logging():
    """Demo ultra-detailed function logging"""
    print("\n🔥 DEMO: Ultra-Detailed Function Logging")
    print("=" * 60)
    
    @log_detailed('DEMO_FUNCTION', include_args=True, include_result=True)
    def calculate_total_price(items, tax_rate=0.08, discount=0):
        """Demo function with ultra-detailed logging"""
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        taxable_amount = subtotal - discount
        tax = taxable_amount * tax_rate
        total = taxable_amount + tax
        return {
            'subtotal': subtotal,
            'tax': tax,
            'discount': discount,
            'total': total
        }
    
    @log_detailed('DEMO_ERROR_FUNCTION', include_args=True, include_result=False)
    def risky_operation(data):
        """Demo function that might fail"""
        if not data:
            raise ValueError("Data cannot be empty!")
        return len(data)
    
    # Test successful function
    items = [
        {'name': 'Product A', 'price': 10.99, 'quantity': 2},
        {'name': 'Product B', 'price': 5.99, 'quantity': 3},
        {'name': 'Product C', 'price': 2.99, 'quantity': 1}
    ]
    
    result = calculate_total_price(items, tax_rate=0.08, discount=5.0)
    print(f"✅ Function result: {result}")
    
    # Test function that fails
    try:
        risky_operation([])
    except ValueError as e:
        print(f"✅ Error properly logged: {e}")
    
    print("✅ Function execution logged with extreme detail!")

def demo_data_changes():
    """Demo ultra-detailed data change logging"""
    print("\n🔥 DEMO: Ultra-Detailed Data Change Logging")
    print("=" * 60)
    
    # Simulate product update
    old_product_data = {
        'name': 'Old Product Name',
        'price': 99.99,
        'stock_level': 50,
        'description': 'Old description',
        'category_id': 1
    }
    
    new_product_data = {
        'name': 'New Product Name',
        'price': 109.99,
        'stock_level': 45,
        'description': 'New description',
        'category_id': 2
    }
    
    log_data_change(
        table_name='products',
        operation='UPDATE',
        record_id=1234,
        old_data=old_product_data,
        new_data=new_product_data,
        user='admin_user',
        reason='Price increase and name change',
        primary_keys={'id': 1234},
        foreign_keys={'category_id': 2},
        transaction_id='txn_123456',
        validation_results={'price_valid': True, 'stock_valid': True}
    )
    
    # Simulate customer creation
    old_customer_data = {}
    new_customer_data = {
        'name': 'New Customer',
        'phone': '123-456-7890',
        'email': 'customer@example.com',
        'type': 'RETAIL',
        'current_credit': 0.0
    }
    
    log_data_change(
        table_name='customers',
        operation='CREATE',
        record_id=5678,
        old_data=old_customer_data,
        new_data=new_customer_data,
        user='admin_user',
        reason='New customer registration',
        primary_keys={'id': 5678},
        foreign_keys={},
        transaction_id='txn_123457'
    )
    
    print("✅ Data changes logged with extreme detail!")

def demo_performance_logging():
    """Demo performance logging"""
    print("\n🔥 DEMO: Ultra-Detailed Performance Logging")
    print("=" * 60)
    
    @log_detailed('PERFORMANCE_TEST')
    def slow_operation():
        """Simulate a slow operation"""
        time.sleep(0.5)  # Simulate 500ms operation
        return "Operation completed"
    
    # Execute and log performance
    result = slow_operation()
    print(f"✅ Performance logged for: {result}")
    
    # Manual performance logging
    start_time = time.time()
    time.sleep(0.2)  # Simulate 200ms database operation
    duration = time.time() - start_time
    
    ultra_logger.log_performance(
        operation='database_query',
        duration=duration,
        memory_before=150000000,  # 150MB
        memory_after=152000000,   # 152MB
        memory_peak=155000000,    # 155MB
        cpu_usage=25.5,
        database_queries=3,
        cache_hits=15,
        cache_misses=2,
        network_requests=1,
        thread_count=4
    )
    
    print("✅ Performance metrics logged!")

def show_log_files():
    """Show the generated log files"""
    print("\n🔥 GENERATED LOG FILES")
    print("=" * 60)
    
    log_dir = "logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.startswith('ultra_detailed_')]
        for log_file in sorted(log_files):
            file_path = os.path.join(log_dir, log_file)
            size = os.path.getsize(file_path)
            print(f"📄 {log_file} ({size:,} bytes)")
    else:
        print("❌ Logs directory not found")
    
    print(f"\n📁 Log files location: {os.path.abspath(log_dir)}")
    print("📝 Open these files to see the ultra-detailed logs!")

def main():
    """Run the complete demo"""
    print("🚀 ULTRA-DETAILED LOGGING DEMO")
    print("=" * 80)
    print("This demo shows the extreme logging capabilities for POS operations")
    print("Every click, stock change, and user interaction is tracked in detail!")
    print("=" * 80)
    
    try:
        # Run all demos
        demo_stock_operations()
        demo_user_interactions()
        demo_function_logging()
        demo_data_changes()
        demo_performance_logging()
        show_log_files()
        
        print("\n🎉 DEMO COMPLETE!")
        print("=" * 60)
        print("✅ All ultra-detailed logging features demonstrated!")
        print("📄 Check the log files to see the detailed output")
        print("🔍 Each log entry contains:")
        print("   • Exact timestamps with microseconds")
        print("   • User information and session data")
        print("   • Complete before/after values")
        print("   • System performance metrics")
        print("   • Error details with stack traces")
        print("   • Mouse positions and keyboard modifiers")
        print("   • Widget properties and states")
        print("   • Database transaction details")
        print("   • And much more!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
