import sys
sys.path.append('.')
from pos_app.database.db_utils import get_db_session
from pos_app.models.database import Product, SaleItem, PurchaseItem
from sqlalchemy import func

with get_db_session() as session:
    zero_stock_products = session.query(Product).filter(Product.stock_level == 0).all()
    
    print('Products that SHOULD have stock but show 0:')
    print('=' * 80)
    
    missing_stock_products = []
    
    for product in zero_stock_products:
        total_purchased = session.query(func.sum(PurchaseItem.quantity)).filter(
            PurchaseItem.product_id == product.id
        ).scalar() or 0
        
        total_sold = session.query(func.sum(SaleItem.quantity)).filter(
            SaleItem.product_id == product.id
        ).scalar() or 0
        
        expected_stock = total_purchased - total_sold
        
        if expected_stock > 0:  # Should have stock but shows 0
            missing_stock_products.append({
                'id': product.id,
                'name': product.name,
                'current_stock': product.stock_level,
                'purchased': total_purchased,
                'sold': total_sold,
                'expected': expected_stock
            })
    
    # Sort by expected stock (highest first)
    missing_stock_products.sort(key=lambda x: x['expected'], reverse=True)
    
    print(f'Total {len(missing_stock_products)} products should have stock but show 0:')
    print()
    
    for i, p in enumerate(missing_stock_products, 1):
        print(f'{i}. ID: {p["id"]}')
        print(f'   Name: {p["name"]}')
        print(f'   Current Stock: {p["current_stock"]}')
        print(f'   Purchased: {p["purchased"]}')
        print(f'   Sold: {p["sold"]}')
        print(f'   Expected Stock: {p["expected"]}')
        print(f'   Missing: {p["expected"]} units')
        print('-' * 50)
    
    print()
    print('SUMMARY:')
    print(f'Total missing stock units: {sum(p["expected"] for p in missing_stock_products)}')
    print('This analysis is READ-ONLY - no changes were made to the database.')
