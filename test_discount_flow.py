#!/usr/bin/env python3
"""Test script to verify customer statement discount data flow"""

import sys
import os
from datetime import datetime, date

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Sale, Customer
    from sqlalchemy.orm import joinedload
    
    print("=== Customer Statement Discount Data Flow Test ===")
    
    # Get database session
    with get_db_session() as session:
        # Find a customer with recent sales that have discounts
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        
        # Find customers with sales that have discounts
        customers_with_discounts = session.query(Customer).join(Sale).filter(
            Sale.customer_id == Customer.id,
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.discount_amount > 0
        ).distinct().all()
        
        print(f"Found {len(customers_with_discounts)} customers with discounted sales today:")
        print()
        
        for customer in customers_with_discounts[:3]:  # Test first 3 customers
            print(f"=== Customer: {customer.name} ===")
            
            # Get their latest sale with discount
            latest_sale = session.query(Sale).filter(
                Sale.customer_id == customer.id,
                Sale.sale_date >= start_dt,
                Sale.sale_date <= end_dt,
                Sale.discount_amount > 0
            ).order_by(Sale.sale_date.desc()).first()
            
            if latest_sale:
                invoice = getattr(latest_sale, 'invoice_number', f'INV-{latest_sale.id}')
                subtotal = getattr(latest_sale, 'subtotal', 0) or 0
                discount = getattr(latest_sale, 'discount_amount', 0) or 0
                total = getattr(latest_sale, 'total_amount', 0) or 0
                
                print(f"  Latest Sale: {invoice}")
                print(f"  Subtotal: Rs {subtotal:.2f}")
                print(f"  Discount: Rs {discount:.2f}")
                print(f"  Total: Rs {total:.2f}")
                print(f"  Expected Total: Rs {subtotal - discount:.2f}")
                
                # Test the data that would be passed to the HTML generation
                test_data = {
                    "total_sales": total,
                    "total_discounts": discount,
                    "balance": getattr(customer, 'current_credit', 0) or 0
                }
                
                print(f"\n  Data passed to HTML generation:")
                print(f"    total_sales: {test_data['total_sales']} (type: {type(test_data['total_sales'])})")
                print(f"    total_discounts: {test_data['total_discounts']} (type: {type(test_data['total_discounts'])})")
                print(f"    balance: {test_data['balance']} (type: {type(test_data['balance'])})")
                
                # Test the discount check logic
                total_discounts = test_data.get('total_discounts', 0)
                try:
                    total_discounts = float(total_discounts) if total_discounts else 0.0
                except (ValueError, TypeError):
                    total_discounts = 0.0
                
                print(f"\n  After conversion:")
                print(f"    total_discounts: {total_discounts}")
                print(f"    Should add discount: {total_discounts > 0}")
                
                if total_discounts > 0:
                    print(f"    Discount card would be: ('Discount Given', 'Rs -{total_discounts:.2f}')")
                
            else:
                print("  No discounted sale found")
            
            print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
