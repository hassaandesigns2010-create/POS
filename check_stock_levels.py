#!/usr/bin/env python3
"""Check stock levels for DALING and SOKANY products"""

import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Product, PurchaseItem, Purchase
    
    with get_db_session() as session:
        # Find DALING LINT REMOVER product
        daling_product = session.query(Product).filter(Product.name.like('%DALING%')).first()
        if daling_product:
            print(f'DALING LINT REMOVER:')
            print(f'  Current Stock: {daling_product.stock_level}')
            print(f'  Purchase Price: {daling_product.purchase_price}')
            print()
        
        # Find SOKANY LINT REMOVER product
        sokany_product = session.query(Product).filter(Product.name.like('%SOKANY%')).first()
        if sokany_product:
            print(f'SOKANY LINT REMOVER SK866:')
            print(f'  Current Stock: {sokany_product.stock_level}')
            print(f'  Purchase Price: {sokany_product.purchase_price}')
            print()
        
        # Also check recent purchase items to see what was received
        recent_items = session.query(PurchaseItem).order_by(PurchaseItem.id.desc()).limit(10).all()
        
        print('Recent Purchase Items:')
        for item in recent_items:
            product = session.query(Product).filter_by(id=item.product_id).first()
            if product and ('DALING' in product.name or 'SOKANY' in product.name):
                purchase = session.query(Purchase).filter_by(id=item.purchase_id).first()
                print(f'{product.name}:')
                print(f'  Purchase ID: {item.purchase_id}')
                print(f'  Quantity: {item.quantity}')
                print(f'  Received Qty: {item.received_quantity}')
                print(f'  Current Stock: {product.stock_level}')
                print(f'  Order Date: {purchase.order_date}')
                print(f'  Delivery Date: {purchase.delivery_date}')
                print(f'  Total Amount: Rs {purchase.total_amount}')
                print()
    
    print('Stock check completed.')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
