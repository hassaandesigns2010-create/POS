#!/usr/bin/env python3
"""Debug script to check customer statement discount issue"""

import sys
import os
from datetime import datetime, date

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Sale, SaleItem, Customer
    from sqlalchemy.orm import joinedload
    
    print("=== Customer Statement Discount Debug ===")
    
    # Get database session
    with get_db_session() as session:
        # Find the sale with 203 total that user mentioned
        # Let's look for recent sales with discounts
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        
        print(f"Searching for sales with discounts on {today}")
        print()
        
        # Find sales with discount_amount > 0
        sales_with_discounts = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.discount_amount > 0
        ).all()
        
        print(f"Found {len(sales_with_discounts)} sales with discounts today:")
        print()
        
        for sale in sales_with_discounts:
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            total = getattr(sale, 'total_amount', 0) or 0
            subtotal = getattr(sale, 'subtotal', 0) or 0
            discount = getattr(sale, 'discount_amount', 0) or 0
            customer_id = getattr(sale, 'customer_id', None)
            
            print(f"Sale: {invoice}")
            print(f"  Customer ID: {customer_id}")
            print(f"  Subtotal: Rs {subtotal:.2f}")
            print(f"  Discount: Rs {discount:.2f}")
            print(f"  Total: Rs {total:.2f}")
            print()
            
            # Check if this sale has items
            items = session.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
            print(f"  Items in sale: {len(items)}")
            
            for i, item in enumerate(items[:3], 1):  # Show first 3 items
                item_total = getattr(item, 'total', 0) or 0
                item_subtotal = getattr(item, 'subtotal', 0) or 0
                print(f"    Item {i}: Total Rs {item_total:.2f}, Subtotal Rs {item_subtotal:.2f}")
            
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more items")
            
            print()
        
        # Now let's find the specific sale that might be showing 203
        # Look for sales where total_amount is around 203
        sales_around_203 = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.total_amount >= 200,
            Sale.total_amount <= 210
        ).all()
        
        print(f"=== Sales around Rs 203 ===")
        for sale in sales_around_203:
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            total = getattr(sale, 'total_amount', 0) or 0
            subtotal = getattr(sale, 'subtotal', 0) or 0
            discount = getattr(sale, 'discount_amount', 0) or 0
            customer_id = getattr(sale, 'customer_id', None)
            
            print(f"Sale: {invoice}")
            print(f"  Customer ID: {customer_id}")
            print(f"  Subtotal: Rs {subtotal:.2f}")
            print(f"  Discount: Rs {discount:.2f}")
            print(f"  Total: Rs {total:.2f}")
            
            # Check if this should be 203 after discount
            if discount > 0:
                expected_total = subtotal - discount
                print(f"  Expected Total: Rs {expected_total:.2f}")
                if abs(expected_total - 203) < 1:
                    print(f"  *** This might be the Rs 203 sale! ***")
            
            print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
