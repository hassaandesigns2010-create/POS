#!/usr/bin/env python3
"""Test script to verify customer statement printing fix"""

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
    
    print("=== Customer Statement Printing Fix Test ===")
    
    # Get database session
    with get_db_session() as session:
        # Find the sale with Rs 152 subtotal and Rs 2 discount (should total Rs 150)
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        
        print(f"Searching for sales with Rs 2 discount on {today}")
        print()
        
        # Find sales with discount_amount = 2
        sales_with_2_discount = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.discount_amount == 2
        ).all()
        
        print(f"Found {len(sales_with_2_discount)} sales with Rs 2 discount today:")
        print()
        
        for sale in sales_with_2_discount:
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            subtotal = getattr(sale, 'subtotal', 0) or 0
            discount = getattr(sale, 'discount_amount', 0) or 0
            total = getattr(sale, 'total_amount', 0) or 0
            customer_id = getattr(sale, 'customer_id', None)
            
            print(f"Sale: {invoice}")
            print(f"  Customer ID: {customer_id}")
            print(f"  Subtotal: Rs {subtotal:.2f}")
            print(f"  Discount: Rs {discount:.2f}")
            print(f"  Total: Rs {total:.2f}")
            print()
            
            # Verify the math
            expected_total = subtotal - discount
            print(f"  Expected Total: Rs {expected_total:.2f}")
            
            if abs(total - expected_total) < 0.01:
                print(f"  ✅ Total is correct!")
            else:
                print(f"  ❌ Total mismatch! Expected Rs {expected_total:.2f}, got Rs {total:.2f}")
            
            # Check items
            items = session.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
            print(f"  Items: {len(items)}")
            
            for i, item in enumerate(items, 1):
                item_total = getattr(item, 'total', 0) or 0
                print(f"    Item {i}: Total Rs {item_total:.2f}")
                
                # Calculate what this item should be after discount
                if subtotal > 0:
                    proportion = item_total / subtotal
                    discounted_amount = total * proportion
                    print(f"           After discount: Rs {discounted_amount:.2f} (proportion: {proportion:.4f})")
            
            print()
        
        # Test the specific case mentioned by user
        print("=== Testing Specific Case (Rs 152 -> Rs 150 with Rs 2 discount) ===")
        
        sales_152_total = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.subtotal == 152,
            Sale.discount_amount == 2
        ).all()
        
        if sales_152_total:
            sale = sales_152_total[0]
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            subtotal = getattr(sale, 'subtotal', 0) or 0
            discount = getattr(sale, 'discount_amount', 0) or 0
            total = getattr(sale, 'total_amount', 0) or 0
            
            print(f"Found target sale: {invoice}")
            print(f"  Subtotal: Rs {subtotal:.2f}")
            print(f"  Discount: Rs {discount:.2f}")
            print(f"  Total: Rs {total:.2f}")
            
            if total == 150:
                print(f"  ✅ Perfect! This sale should print as Rs 150 total with Rs 2 discount line")
            else:
                print(f"  ❌ Expected Rs 150, but got Rs {total}")
        else:
            print("No sale found with Rs 152 subtotal and Rs 2 discount")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
