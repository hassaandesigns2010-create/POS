#!/usr/bin/env python3
"""Check for duplicate purchase items in recent purchases"""

import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from pos_app.database.db_utils import get_db_session
    from pos_app.models.database import Purchase, PurchaseItem, Product
    
    with get_db_session() as session:
        # Check the most recent purchases
        recent_purchases = session.query(Purchase).order_by(Purchase.id.desc()).limit(3).all()
        
        for purchase in recent_purchases:
            print(f'=== Purchase ID: {purchase.id} ===')
            print(f'Status: {purchase.status}')
            print(f'Order Date: {purchase.order_date}')
            print(f'Delivery Date: {purchase.delivery_date}')
            
            # Get all items for this purchase
            items = session.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase.id).all()
            print(f'Items: {len(items)}')
            
            # Group items by product
            product_items = {}
            for item in items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                if product:
                    product_name = product.name
                    if product_name not in product_items:
                        product_items[product_name] = []
                    product_items[product_name].append(item)
            
            # Check for duplicates
            for product_name, items_list in product_items.items():
                if len(items_list) > 1:
                    print(f'  DUPLICATE FOUND: {product_name}')
                    total_qty = sum(item.quantity for item in items_list)
                    print(f'    Total quantity ordered: {total_qty}')
                    for i, item in enumerate(items_list):
                        print(f'      Item {i+1}: Qty {item.quantity}, Received {item.received_quantity}')
                else:
                    item = items_list[0]
                    print(f'  {product_name}: Qty {item.quantity}, Received {item.received_quantity}')
            
            print()
    
    print('Duplicate check completed.')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
