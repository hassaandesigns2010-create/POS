#!/usr/bin/env python3
"""
Analyze products with 0 stock to check if their stock should be zero
This script only reads data - no changes made
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from pos_app.models.database import get_db_session, Product, SaleItem, PurchaseItem
from sqlalchemy import func
from decimal import Decimal

def analyze_zero_stock_products():
    """Analyze all products with 0 stock"""
    
    with get_db_session() as session:
        # Get all products with 0 stock
        zero_stock_products = session.query(Product).filter(Product.stock_level == 0).all()
        
        print(f'Found {len(zero_stock_products)} products with 0 stock')
        print('=' * 80)
        
        correct_count = 0
        missing_count = 0
        oversold_count = 0
        
        for product in zero_stock_products:
            print(f'\nProduct ID: {product.id}')
            print(f'Name: {product.name}')
            print(f'Current Stock: {product.stock_level}')
            print(f'Reorder Level: {product.reorder_level}')
            print(f'Unit Price: Rs {product.unit_price or 0}')
            
            # Calculate total purchased
            total_purchased = session.query(func.sum(PurchaseItem.quantity)).filter(
                PurchaseItem.product_id == product.id
            ).scalar() or 0
            
            # Calculate total sold
            total_sold = session.query(func.sum(SaleItem.quantity)).filter(
                SaleItem.product_id == product.id
            ).scalar() or 0
            
            print(f'Total Purchased: {total_purchased}')
            print(f'Total Sold: {total_sold}')
            print(f'Expected Stock: {total_purchased - total_sold}')
            
            # Analysis
            expected_stock = total_purchased - total_sold
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
        
        # Summary
        print(f'\n\nSUMMARY:')
        print(f'=' * 80)
        print(f'Total products with 0 stock: {len(zero_stock_products)}')
        print(f'Correctly at 0 stock: {correct_count}')
        print(f'Should have stock (missing): {missing_count}')
        print(f'Oversold (negative expected): {oversold_count}')
        
        if missing_count > 0:
            print(f'\n⚠ WARNING: {missing_count} products should have stock but show 0')
        if oversold_count > 0:
            print(f'\n⚠ WARNING: {oversold_count} products have been oversold')
        
        print('\nThis analysis is READ-ONLY - no changes were made to the database.')

if __name__ == '__main__':
    analyze_zero_stock_products()
