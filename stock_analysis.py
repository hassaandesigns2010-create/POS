from pos_app.models.database import get_db_session, Product, SaleItem, PurchaseItem
from sqlalchemy import func

with get_db_session() as session:
    zero_stock_products = session.query(Product).filter(Product.stock_level == 0).all()
    
    print(f'Found {len(zero_stock_products)} products with 0 stock')
    print('=' * 80)
    
    correct_count = 0
    missing_count = 0
    oversold_count = 0
    
    for product in zero_stock_products:
        total_purchased = session.query(func.sum(PurchaseItem.quantity)).filter(
            PurchaseItem.product_id == product.id
        ).scalar() or 0
        
        total_sold = session.query(func.sum(SaleItem.quantity)).filter(
            SaleItem.product_id == product.id
        ).scalar() or 0
        
        expected_stock = total_purchased - total_sold
        
        print(f'Product ID: {product.id}')
        print(f'Name: {product.name}')
        print(f'Current Stock: {product.stock_level}')
        print(f'Total Purchased: {total_purchased}')
        print(f'Total Sold: {total_sold}')
        print(f'Expected Stock: {expected_stock}')
        
        if expected_stock == 0:
            print('✓ Stock should be 0 - CORRECT')
            correct_count += 1
        elif expected_stock > 0:
            print(f'⚠ Stock should be {expected_stock} - MISSING STOCK')
            missing_count += 1
        else:
            print(f'⚠ Stock should be {expected_stock} - OVERSOLD')
            oversold_count += 1
        
        print('-' * 40)
    
    print(f'\nSUMMARY:')
    print(f'Total products with 0 stock: {len(zero_stock_products)}')
    print(f'Correctly at 0 stock: {correct_count}')
    print(f'Should have stock (missing): {missing_count}')
    print(f'Oversold (negative expected): {oversold_count}')
    print('\nThis analysis is READ-ONLY - no changes were made to the database.')
