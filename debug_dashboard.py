#!/usr/bin/env python3
"""Debug script to compare dashboard vs database calculations"""

import sys
import os
from datetime import datetime, date

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Sale
    from sqlalchemy import and_, or_
    
    print("=== Dashboard vs Database Comparison ===")
    print(f"Today's date: {date.today()}")
    print()
    
    # Get database session
    with get_db_session() as session:
        # Use same date range as dashboard
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        
        print(f"Querying sales from {start_dt} to {end_dt}")
        print()
        
        # Dashboard query for normal sales
        normal_sales = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.is_refund != True,
            or_(Sale.status == 'COMPLETED', Sale.status == 'REFUNDED', Sale.status == None)
        ).all()
        
        # Dashboard query for refunds
        refunds = session.query(Sale).filter(
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt,
            Sale.is_refund == True,
            or_(Sale.status == 'COMPLETED', Sale.status == 'REFUNDED', Sale.status == None)
        ).all()
        
        print(f"=== DASHBOARD METHOD ===")
        print(f"Normal sales found: {len(normal_sales)}")
        print(f"Refunds found: {len(refunds)}")
        print()
        
        # Calculate totals using dashboard method
        from decimal import Decimal
        total_normal_sales = sum(Decimal(str(s.total_amount or 0)) for s in normal_sales if s.total_amount is not None)
        total_refunds = sum(abs(Decimal(str(s.total_amount or 0))) for s in refunds if s.total_amount is not None)
        total_sales_dashboard = total_normal_sales - total_refunds
        
        print(f"Normal sales total: Rs {total_normal_sales:.2f}")
        print(f"Refunds total: Rs {total_refunds:.2f}")
        print(f"Dashboard net total: Rs {total_sales_dashboard:.2f}")
        print()
        
        # Show individual normal sales
        print("=== NORMAL SALES (Dashboard Method) ===")
        for i, sale in enumerate(normal_sales[:10], 1):  # Show first 10
            invoice = getattr(sale, 'invoice_number', f'INV-{sale.id}')
            total = sale.total_amount or 0
            status = getattr(sale, 'status', 'None')
            print(f"{i:2d}. {invoice} - Rs {total:.2f} - Status: {status}")
        
        if len(normal_sales) > 10:
            print(f"... and {len(normal_sales) - 10} more")
        print()
        
        # Show individual refunds
        print("=== REFUNDS (Dashboard Method) ===")
        for i, refund in enumerate(refunds[:10], 1):  # Show first 10
            invoice = getattr(refund, 'invoice_number', f'INV-{refund.id}')
            total = refund.total_amount or 0
            status = getattr(refund, 'status', 'None')
            print(f"{i:2d}. {invoice} - Rs {total:.2f} - Status: {status}")
        
        if len(refunds) > 10:
            print(f"... and {len(refunds) - 10} more")
        print()
        
        # Now check our original database method
        print("=== ORIGINAL DATABASE METHOD ===")
        today_sales = session.query(Sale).filter(
            and_(
                Sale.sale_date >= start_dt,
                Sale.sale_date <= end_dt,
                Sale.is_refund == False  # Exclude refunds
            )
        ).all()
        
        today_refunds = session.query(Sale).filter(
            and_(
                Sale.sale_date >= start_dt,
                Sale.sale_date <= end_dt,
                Sale.is_refund == True  # Only refunds
            )
        ).all()
        
        total_amount = sum(sale.total_amount or 0 for sale in today_sales)
        refund_total = sum(refund.total_amount or 0 for refund in today_refunds)
        net_sales_db = total_amount - refund_total
        
        print(f"Normal sales (original): {len(today_sales)}")
        print(f"Refunds (original): {len(today_refunds)}")
        print(f"Original net total: Rs {net_sales_db:.2f}")
        print()
        
        print("=== COMPARISON ===")
        print(f"Dashboard method: Rs {total_sales_dashboard:.2f}")
        print(f"Original method: Rs {net_sales_db:.2f}")
        print(f"Difference: Rs {abs(float(total_sales_dashboard) - float(net_sales_db)):.2f}")
        
        if abs(float(total_sales_dashboard) - float(net_sales_db)) < 1:
            print("✅ Both methods match!")
        else:
            print("❌ Methods don't match - investigating...")
            
            # Check for differences in sales counts
            if len(normal_sales) != len(today_sales):
                print(f"❌ Sales count difference: Dashboard={len(normal_sales)}, Original={len(today_sales)}")
            
            # Check for differences in refund counts  
            if len(refunds) != len(today_refunds):
                print(f"❌ Refund count difference: Dashboard={len(refunds)}, Original={len(today_refunds)}")
            
            # Check for status differences
            print("\n=== STATUS ANALYSIS ===")
            print("Normal sales with different statuses:")
            for sale in normal_sales:
                status = getattr(sale, 'status', 'None')
                if status not in ['COMPLETED', None]:
                    print(f"  {getattr(sale, 'invoice_number', f'INV-{sale.id}')} - Status: {status}")
            
            print("\nRefunds with different statuses:")
            for refund in refunds:
                status = getattr(refund, 'status', 'None')
                if status not in ['COMPLETED', 'REFUNDED', None]:
                    print(f"  {getattr(refund, 'invoice_number', f'INV-{refund.id}')} - Status: {status}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
