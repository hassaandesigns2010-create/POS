#!/usr/bin/env python3
"""
Quick Stock Fix - Focus on products that should have stock but show zero
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_zero_stock_products():
    """Fix products that have zero stock but should have stock based on latest backup"""
    
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'pos_network',
        'user': 'admin',
        'password': 'admin'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("QUICK STOCK FIX - PRODUCTS WITH ZERO STOCK")
        print("=" * 80)
        
        # Get products with zero stock
        query = """
        SELECT id, name, sku, barcode, stock_level, purchase_price, retail_price
        FROM products 
        WHERE stock_level = 0 OR stock_level IS NULL
        ORDER BY name
        """
        
        cursor.execute(query)
        zero_stock_products = cursor.fetchall()
        
        print(f"Found {len(zero_stock_products)} products with zero stock")
        
        # Read latest backup to get expected stock
        backup_file = "C:/Users/pc/Documents/backups/pos_backup_20260126_192834.sql"
        
        print(f"\nReading backup file: {backup_file}")
        
        # Simple approach: look for product lines with stock > 0
        expected_stock = {}
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            in_copy_section = False
            
            for line in lines:
                if "COPY public.products" in line and "stock_level" in line:
                    in_copy_section = True
                    continue
                
                if in_copy_section and line.strip() == "\\.":
                    break
                
                if in_copy_section and line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 12:  # stock_level is around 12th position
                        try:
                            product_id = parts[0]
                            stock_level = parts[11]  # Approximate position of stock_level
                            
                            # Clean up the stock value
                            if stock_level and stock_level != '\\N':
                                stock_val = float(stock_level.strip('"'))
                                if stock_val > 0:
                                    expected_stock[product_id] = stock_val
                        except:
                            pass
        
        except Exception as e:
            print(f"Error reading backup: {e}")
            return
        
        print(f"Found {len(expected_stock)} products with expected stock > 0 in backup")
        
        # Find discrepancies
        discrepancies = []
        
        for product in zero_stock_products:
            product_id = str(product['id'])
            if product_id in expected_stock:
                discrepancies.append({
                    'id': product['id'],
                    'name': product['name'],
                    'sku': product['sku'],
                    'current_stock': 0,
                    'expected_stock': expected_stock[product_id]
                })
        
        print(f"\n🚨 Found {len(discrepancies)} products that should have stock but show zero:")
        
        if discrepancies:
            # Show top 20
            for i, disc in enumerate(discrepancies[:20], 1):
                print(f"{i}. ID: {disc['id']} - {disc['name'][:40]}")
                print(f"   Should have: {disc['expected_stock']} units, Currently: 0")
                print()
            
            if len(discrepancies) > 20:
                print(f"... and {len(discrepancies) - 20} more products")
            
            # Ask to fix
            print(f"\nDo you want to fix all {len(discrepancies)} products? (y/n)")
            response = input("Enter choice: ").strip().lower()
            
            if response == 'y':
                fixed_count = 0
                
                for disc in discrepancies:
                    try:
                        update_query = """
                        UPDATE products 
                        SET stock_level = %s 
                        WHERE id = %s
                        """
                        cursor.execute(update_query, (disc['expected_stock'], disc['id']))
                        fixed_count += 1
                        
                        if fixed_count <= 10:  # Show first 10 fixes
                            print(f"✅ Fixed: {disc['name'][:30]} - Stock set to {disc['expected_stock']}")
                    
                    except Exception as e:
                        print(f"❌ Error fixing {disc['id']}: {e}")
                
                conn.commit()
                print(f"\n🎉 Successfully fixed {fixed_count} products!")
                
                # Verify fixes
                cursor.execute("SELECT COUNT(*) FROM products WHERE stock_level > 0")
                products_with_stock = cursor.fetchone()[0]
                print(f"📊 Now {products_with_stock} products have stock")
        
        else:
            print("✅ No products found that should have stock but show zero")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    fix_zero_stock_products()
