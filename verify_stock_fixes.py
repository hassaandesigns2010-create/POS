#!/usr/bin/env python3
"""
Verify that stock fixes were applied correctly
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def verify_fixes():
    """Verify the stock fixes were applied correctly"""
    
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
        print("STOCK FIX VERIFICATION REPORT")
        print("=" * 80)
        
        # Check the specific products that were fixed
        fixed_product_ids = [720, 363, 206, 1275, 884, 975, 1359, 331, 1182, 153, 881, 540, 488, 212, 210]
        
        print("Checking the 15 products that were fixed:")
        print("-" * 50)
        
        query = """
        SELECT id, name, sku, stock_level, purchase_price, retail_price
        FROM products 
        WHERE id = ANY(%s)
        ORDER BY name
        """
        
        cursor.execute(query, (fixed_product_ids,))
        fixed_products = cursor.fetchall()
        
        total_stock_restored = 0
        
        for product in fixed_products:
            stock = float(product['stock_level'] or 0)
            if stock > 0:
                total_stock_restored += stock
                print(f"✅ ID: {product['id']} - {product['name'][:40]}")
                print(f"   Stock: {stock} units")
                print(f"   SKU: {product['sku']}")
                print()
            else:
                print(f"❌ ID: {product['id']} - {product['name'][:40]}")
                print(f"   Stock: {stock} units (STILL ZERO!)")
                print()
        
        print(f"📊 Total stock restored: {total_stock_restored:,.0f} units")
        
        # Overall database stats
        cursor.execute("SELECT COUNT(*) FROM products WHERE stock_level > 0")
        products_with_stock = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(stock_level) FROM products WHERE stock_level > 0")
        total_stock = cursor.fetchone()[0] or 0
        
        print(f"\n📦 Current Database Status:")
        print(f"   Total Products: {total_products}")
        print(f"   Products with Stock: {products_with_stock}")
        print(f"   Total Stock: {total_stock:,.0f} units")
        print(f"   Average Stock per Product: {total_stock / products_with_stock:.2f}" if products_with_stock > 0 else "")
        
        # Check for remaining zero-stock products that might need attention
        cursor.execute("""
        SELECT id, name, sku, purchase_price, retail_price
        FROM products 
        WHERE stock_level = 0 OR stock_level IS NULL
        AND purchase_price > 0
        ORDER BY retail_price DESC
        LIMIT 10
        """)
        
        remaining_zero_stock = cursor.fetchall()
        
        if remaining_zero_stock:
            print(f"\n⚠️  Top 10 remaining products with zero stock (that have prices):")
            for product in remaining_zero_stock:
                print(f"   ID: {product['id']} - {product['name'][:40]}")
                print(f"      Price: ${product['retail_price']:.2f}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Stock fix verification complete!")
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    verify_fixes()
