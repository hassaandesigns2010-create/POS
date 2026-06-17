#!/usr/bin/env python3
"""
Simple script to check products with zero stock and identify discrepancies
"""

import os
import sys

def check_zero_stock_products():
    """Check products with zero stock and compare with backup data"""
    
    # Try to connect to database directly
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Database connection parameters
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_network',
            'user': 'admin',
            'password': 'admin'
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("CHECKING PRODUCTS WITH ZERO STOCK")
        print("=" * 80)
        
        # Get products with zero stock
        query = """
        SELECT id, name, sku, barcode, stock_level 
        FROM products 
        WHERE stock_level = 0 OR stock_level IS NULL
        ORDER BY name
        LIMIT 20
        """
        
        cursor.execute(query)
        zero_stock_products = cursor.fetchall()
        
        print(f"Found {len(zero_stock_products)} products with zero stock:")
        print()
        
        for i, product in enumerate(zero_stock_products, 1):
            print(f"{i}. ID: {product['id']}")
            print(f"   Name: {product['name']}")
            print(f"   SKU: {product['sku']}")
            print(f"   Barcode: {product['barcode']}")
            print(f"   Stock: {product['stock_level']}")
            print()
        
        # Now check backup data for these products
        print("\n" + "=" * 80)
        print("CHECKING BACKUP DATA FOR THESE PRODUCTS")
        print("=" * 80)
        
        # Read the latest backup
        backup_file = "C:/Users/pc/Documents/backups/pos_backup_20260126_192834.sql"
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                backup_content = f.read()
            
            # Check each product
            discrepancies = []
            
            for product in zero_stock_products:
                product_id = str(product['id'])
                
                # Look for this product in backup
                # Search for COPY data lines that contain this product ID
                import re
                
                # Pattern to find the product line in COPY section
                pattern = rf'^{re.escape(product_id)}\t([^\t]+)\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([^\t]+)'
                
                matches = re.findall(pattern, backup_content, re.MULTILINE)
                
                if matches:
                    for match in matches:
                        backup_name = match[0].strip('"')
                        backup_stock = match[1].strip()
                        
                        try:
                            backup_stock_val = float(backup_stock)
                            if backup_stock_val > 0:
                                discrepancies.append({
                                    'id': product['id'],
                                    'name': product['name'],
                                    'backup_name': backup_name,
                                    'current_stock': 0,
                                    'backup_stock': backup_stock_val
                                })
                        except:
                            pass
            
            # Show discrepancies
            if discrepancies:
                print(f"Found {len(discrepancies)} products that should have stock:")
                print()
                
                for disc in discrepancies:
                    print(f"ID: {disc['id']}")
                    print(f"Name: {disc['name']}")
                    print(f"Current Stock: {disc['current_stock']}")
                    print(f"Should Be: {disc['backup_stock']}")
                    print()
                
                # Ask to fix
                print("Do you want to fix these stock levels? (y/n)")
                input("Press Enter to continue with fixes...")
                
                # Fix the stock levels
                for disc in discrepancies:
                    update_query = """
                    UPDATE products 
                    SET stock_level = %s 
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (disc['backup_stock'], disc['id']))
                    print(f"Fixed: {disc['name']} - Stock set to {disc['backup_stock']}")
                
                conn.commit()
                print(f"\nSuccessfully fixed {len(discrepancies)} products!")
                
            else:
                print("No discrepancies found. All zero-stock products should be zero.")
        
        except Exception as e:
            print(f"Error reading backup file: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_zero_stock_products()
