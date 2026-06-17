#!/usr/bin/env python3
"""Check stock calculation for DALING and SOKANY products"""

import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Product, Purchase, PurchaseItem
    
    with get_db_session() as session:
        # Get current stock levels
        daling_product = session.query(Product).filter(Product.name.like('%DALING%')).first()
        sokany_product = session.query(Product).filter(Product.name.like('%SOKANY%')).first()
        
        print('=== Current Stock Analysis ===')
        if daling_product:
            print(f'DALING LINT REMOVER: {daling_product.stock_level}')
        if sokany_product:
            print(f'SOKANY LINT REMOVER SK866: {sokany_product.stock_level}')
        print()
        
        # Get all purchase items for these products
        print('=== All Purchase Items ===')
        
        # Find all purchase items for DALING
        if daling_product:
            daling_items = session.query(PurchaseItem).filter(PurchaseItem.product_id == daling_product.id).all()
            print(f'DALING LINT REMOVER purchase history:')
            for item in daling_items:
                purchase = session.query(Purchase).filter_by(id=item.purchase_id).first()
                print(f'  Purchase {item.purchase_id}: Qty {item.quantity}, Received {item.received_quantity}, Date {purchase.order_date}')
            print()
        
        # Find all purchase items for SOKANY
        if sokany_product:
            sokany_items = session.query(PurchaseItem).filter(PurchaseItem.product_id == sokany_product.id).all()
            print(f'SOKANY LINT REMOVER SK866 purchase history:')
            for item in sokany_items:
                purchase = session.query(Purchase).filter_by(id=item.purchase_id).first()
                print(f'  Purchase {item.purchase_id}: Qty {item.quantity}, Received {item.received_quantity}, Date {purchase.order_date}')
            print()
        
        # Calculate expected stock if received only once
        print('=== Stock Calculation ===')
        if daling_product:
            # Find the most recent purchase for DALING
            recent_daling = session.query(PurchaseItem).filter(PurchaseItem.product_id == daling_product.id).order_by(PurchaseItem.id.desc()).first()
            if recent_daling:
                expected_stock = recent_daling.quantity  # Assuming it started from 0
                actual_stock = daling_product.stock_level
                print(f'DALING: Expected {expected_stock}, Actual {actual_stock}')
                if actual_stock > expected_stock:
                    print(f'  Stock was added {actual_stock - expected_stock} extra times!')
        
        if sokany_product:
            # Find the most recent purchase for SOKANY
            recent_sokany = session.query(PurchaseItem).filter(PurchaseItem.product_id == sokany_product.id).order_by(PurchaseItem.id.desc()).first()
            if recent_sokany:
                expected_stock = recent_sokany.quantity  # Assuming it started from 0
                actual_stock = sokany_product.stock_level
                print(f'SOKANY: Expected {expected_stock}, Actual {actual_stock}')
                if actual_stock > expected_stock:
                    print(f'  Stock was added {actual_stock - expected_stock} extra times!')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
