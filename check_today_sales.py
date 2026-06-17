#!/usr/bin/env python3
"""Script to check today's sales data in database"""

import sys
import os
from datetime import datetime, date

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Sale, SaleItem
    from sqlalchemy import func, and_
    
    print("=== Today's Sales Database Check ===")
    print(f"Today's date: {date.today()}")
    print()
    
    # Get database session
    with get_db_session() as session:
        # Get today's date range
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        print(f"Querying sales from {start_of_day} to {end_of_day}")
        print()
        
        # Query today's sales (excluding refunds)
        today_sales = session.query(Sale).filter(
            and_(
                Sale.sale_date >= start_of_day,
                Sale.sale_date <= end_of_day,
                Sale.is_refund == False  # Exclude refunds
            )
        ).all()
        
        print(f"Found {len(today_sales)} non-refund sales for today")
        print()
        
        # Calculate totals
        total_amount = sum(sale.total_amount or 0 for sale in today_sales)
        total_subtotal = sum(sale.subtotal or 0 for sale in today_sales)
        total_discount = sum(sale.discount_amount or 0 for sale in today_sales)
        
        print("=== SALES BREAKDOWN ===")
        print(f"Total Sales (before discount): Rs {total_subtotal:.2f}")
        print(f"Total Discounts: Rs {total_discount:.2f}")
        print(f"Total Net Sales (after discount): Rs {total_amount:.2f}")
        print()
        
        # Show individual sales
        print("=== INDIVIDUAL SALES ===")
        for i, sale in enumerate(today_sales, 1):
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            customer_name = getattr(sale.customer, 'name', 'Walk-in') if sale.customer else 'Walk-in'
            subtotal = sale.subtotal or 0
            discount = sale.discount_amount or 0
            total = sale.total_amount or 0
            
            print(f"{i:2d}. {invoice} - {customer_name}")
            print(f"    Subtotal: Rs {subtotal:.2f}, Discount: Rs {discount:.2f}, Total: Rs {total:.2f}")
            
            # Show items if any
            if hasattr(sale, 'items') and sale.items:
                for j, item in enumerate(sale.items, 1):
                    product_name = getattr(item.product, 'name', 'Unknown') if item.product else 'Unknown'
                    qty = item.quantity or 1
                    price = item.unit_price or 0
                    item_total = getattr(item, 'total', qty * price) or (qty * price)
                    print(f"      {j}. {product_name} x{qty} @ Rs {price:.2f} = Rs {item_total:.2f}")
            print()
        
        # Also check refunds separately
        today_refunds = session.query(Sale).filter(
            and_(
                Sale.sale_date >= start_of_day,
                Sale.sale_date <= end_of_day,
                Sale.is_refund == True  # Only refunds
            )
        ).all()
        
        if today_refunds:
            refund_total = sum(refund.total_amount or 0 for refund in today_refunds)
            print(f"=== REFUNDS ===")
            print(f"Found {len(today_refunds)} refunds for today")
            print(f"Total Refunds: Rs {refund_total:.2f}")
            print()
            
            print("=== INDIVIDUAL REFUNDS ===")
            for i, refund in enumerate(today_refunds, 1):
                invoice = getattr(refund, 'invoice_number', f'INV-{refund.id}')
                customer_name = getattr(refund.customer, 'name', 'Walk-in') if refund.customer else 'Walk-in'
                total = refund.total_amount or 0
                
                print(f"{i:2d}. {invoice} - {customer_name} - Refund: Rs {total:.2f}")
            print()
            
            print("=== NET TOTALS ===")
            print(f"Net Sales (Sales - Refunds): Rs {total_amount - refund_total:.2f}")
        else:
            print("=== NO REFUNDS TODAY ===")
            print()
            print("=== FINAL TOTAL ===")
            print(f"Final Total Sales: Rs {total_amount:.2f}")
        
        print()
        print("=== COMPARISON ===")
        print(f"Dashboard shows: Rs 170,980.00")
        print(f"Reports shows: Rs 173,435.00")
        print(f"Database shows: Rs {total_amount:.2f}")
        print()
        
        if abs(total_amount - 170980) < 1:
            print("✅ Dashboard amount matches database!")
        elif abs(total_amount - 173435) < 1:
            print("✅ Reports amount matches database!")
        else:
            print("❌ Neither dashboard nor reports match database!")
            print(f"Difference from Dashboard: Rs {abs(total_amount - 170980):.2f}")
            print(f"Difference from Reports: Rs {abs(total_amount - 173435):.2f}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
