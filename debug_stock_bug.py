#!/usr/bin/env python3
"""
Debug the stock calculation bug where selling 1 item makes stock go from 10 to 0
"""

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta

def load_db_config():
    """Load database configuration"""
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'database.json')
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_system',
            'username': 'postgres',
            'password': 'admin'
        }

def connect_to_postgres():
    """Connect to PostgreSQL"""
    config = load_db_config()
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password']
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def analyze_recent_stock_changes(conn):
    """Analyze recent stock changes to find the bug"""
    print("=== RECENT STOCK CHANGES ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Check recent sales that might have affected stock incorrectly
        cursor.execute("""
            SELECT 
                s.id as sale_id,
                s.created_at as sale_time,
                si.product_id,
                p.name as product_name,
                p.stock_level as current_stock,
                si.quantity as sold_quantity,
                si.unit_price,
                s.customer_id
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE s.created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY s.created_at DESC
            LIMIT 20
        """)
        
        recent_sales = cursor.fetchall()
        print(f"📊 Recent sales (last 24 hours):")
        
        for sale in recent_sales:
            sale_id, sale_time, product_id, product_name, current_stock, sold_qty, unit_price, customer_id = sale
            print(f"  Sale #{sale_id} | {sale_time}")
            print(f"    Product: {product_name[:40]:40s} | ID: {product_id}")
            print(f"    Sold: {sold_qty} units | Current stock: {current_stock}")
            print(f"    Price: {unit_price:.2f} | Customer: {customer_id}")
            print()
        
        # Look for stock movements
        cursor.execute("""
            SELECT 
                sm.id,
                sm.created_at,
                sm.product_id,
                p.name as product_name,
                p.stock_level as current_stock,
                sm.movement_type,
                sm.quantity,
                sm.reference_type,
                sm.reference_id,
                sm.notes
            FROM stock_movements sm
            JOIN products p ON sm.product_id = p.id
            WHERE sm.created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY sm.created_at DESC
            LIMIT 20
        """)
        
        movements = cursor.fetchall()
        print(f"📦 Recent stock movements (last 24 hours):")
        
        for movement in movements:
            mov_id, mov_time, product_id, product_name, current_stock, mov_type, qty, ref_type, ref_id, notes = movement
            print(f"  Movement #{mov_id} | {mov_time}")
            print(f"    Product: {product_name[:40]:40s} | ID: {product_id}")
            print(f"    Type: {mov_type} | Quantity: {qty}")
            print(f"    Reference: {ref_type} #{ref_id}")
            print(f"    Current stock: {current_stock}")
            if notes:
                print(f"    Notes: {notes}")
            print()
        
        return recent_sales, movements
        
    except Exception as e:
        print(f"❌ Error analyzing recent changes: {e}")
        return [], []

def check_stock_calculation_bug(conn):
    """Look for specific patterns that indicate the bug"""
    print("=== STOCK CALCULATION BUG DETECTION ===")
    
    try:
        cursor = conn.cursor()
        
        # Check for products with very low stock that might have been affected
        cursor.execute("""
            SELECT 
                id, name, stock_level, retail_price, barcode
            FROM products 
            WHERE stock_level >= 0 AND stock_level <= 5
            ORDER BY stock_level ASC
            LIMIT 15
        """)
        
        low_stock_products = cursor.fetchall()
        print(f"🔍 Products with very low stock (0-5):")
        
        for product in low_stock_products:
            prod_id, name, stock, price, barcode = product
            print(f"  ID:{prod_id:4d} | Stock:{stock:6.1f} | {name[:40]:40s} | {barcode:12s}")
        
        # Check for any negative stock that was fixed
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM products 
            WHERE stock_level < 0
        """)
        
        negative_count = cursor.fetchone()[0]
        if negative_count > 0:
            print(f"\n⚠️  Found {negative_count} products with negative stock!")
            
            cursor.execute("""
                SELECT id, name, stock_level
                FROM products 
                WHERE stock_level < 0
                LIMIT 10
            """)
            
            negative_products = cursor.fetchall()
            for prod in negative_products:
                print(f"  ID:{prod[0]} | {prod[1][:40]:40s} | Stock: {prod[2]}")
        
    except Exception as e:
        print(f"❌ Error checking bug patterns: {e}")

def analyze_business_logic():
    """Analyze the business logic code for potential bugs"""
    print("=== BUSINESS LOGIC ANALYSIS ===")
    
    # Read the business logic file to find potential issues
    business_logic_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_logic_file, 'r') as f:
            content = f.read()
        
        print("🔍 Checking for potential stock calculation bugs...")
        
        # Look for stock update patterns
        lines = content.split('\n')
        stock_update_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'stock_level' in line and ('=' in line or '-=' in line or '+=' in line):
                stock_update_lines.append((i, line.strip()))
        
        print(f"📝 Found {len(stock_update_lines)} stock update operations:")
        for line_num, line_content in stock_update_lines:
            print(f"  Line {line_num}: {line_content}")
        
        # Look for potential issues
        potential_issues = []
        
        if 'stock_level = stock_level - quantity' in content:
            potential_issues.append("Direct subtraction without proper validation")
        
        if 'stock_level *=' in content or 'stock_level /=' in content:
            potential_issues.append("Multiplication/division operations on stock")
        
        if 'stock_level = 0' in content:
            potential_issues.append("Direct assignment of zero to stock")
        
        if potential_issues:
            print(f"\n⚠️  Potential issues found:")
            for issue in potential_issues:
                print(f"  • {issue}")
        else:
            print(f"\n✅ No obvious stock calculation issues found in code")
        
    except Exception as e:
        print(f"❌ Error analyzing business logic: {e}")

def check_for_data_type_issues(conn):
    """Check for data type issues that might cause stock problems"""
    print("=== DATA TYPE ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Check stock_level data types and values
        cursor.execute("""
            SELECT 
                stock_level,
                COUNT(*) as count,
                MIN(stock_level) as min_val,
                MAX(stock_level) as max_val,
                AVG(stock_level) as avg_val
            FROM products 
            GROUP BY stock_level
            ORDER BY count DESC
            LIMIT 10
        """)
        
        stock_distribution = cursor.fetchall()
        print(f"📊 Stock value distribution:")
        
        for stock_val, count, min_val, max_val, avg_val in stock_distribution:
            print(f"  Stock: {stock_val:8.1f} | Count: {count:4d} products")
        
        # Check for any NULL or invalid stock values
        cursor.execute("""
            SELECT COUNT(*) as null_count
            FROM products 
            WHERE stock_level IS NULL
        """)
        
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"\n⚠️  Found {null_count} products with NULL stock!")
        
        # Check for very small fractional values that might indicate precision issues
        cursor.execute("""
            SELECT COUNT(*) as tiny_count
            FROM products 
            WHERE stock_level > 0 AND stock_level < 0.01
        """)
        
        tiny_count = cursor.fetchone()[0]
        if tiny_count > 0:
            print(f"⚠️  Found {tiny_count} products with tiny fractional stock (< 0.01)")
        
    except Exception as e:
        print(f"❌ Error checking data types: {e}")

def create_test_scenario(conn):
    """Create a test scenario to reproduce the bug"""
    print("=== TEST SCENARIO ===")
    
    try:
        cursor = conn.cursor()
        
        # Find a product with decent stock to test with
        cursor.execute("""
            SELECT id, name, stock_level
            FROM products 
            WHERE stock_level >= 10
            ORDER BY stock_level DESC
            LIMIT 5
        """)
        
        test_products = cursor.fetchall()
        
        if test_products:
            print(f"🧪 Found products for testing:")
            for prod in test_products:
                print(f"  ID:{prod[0]} | {prod[1][:40]:40s} | Stock: {prod[2]}")
            
            # Simulate what happens during a sale
            test_product = test_products[0]
            product_id, product_name, original_stock = test_product
            
            print(f"\n🔬 Testing with: {product_name}")
            print(f"   Original stock: {original_stock}")
            
            # Simulate the business logic calculation
            quantity_to_sell = 1
            
            # This is what should happen
            expected_new_stock = original_stock - quantity_to_sell
            print(f"   Expected stock after selling {quantity_to_sell}: {expected_new_stock}")
            
            # Check current stock in database
            cursor.execute(f"SELECT stock_level FROM products WHERE id = {product_id}")
            current_stock = cursor.fetchone()[0]
            print(f"   Actual current stock: {current_stock}")
            
            if current_stock != original_stock:
                print(f"   ⚠️  Stock has changed since we checked!")
                print(f"   This suggests other operations are affecting stock")
            
        else:
            print(f"❌ No products with sufficient stock found for testing")
        
    except Exception as e:
        print(f"❌ Error creating test scenario: {e}")

def main():
    print("=" * 70)
    print("🐛 STOCK CALCULATION BUG INVESTIGATION")
    print("=" * 70)
    print(f"Started at: {datetime.now()}")
    
    conn = connect_to_postgres()
    if not conn:
        print("❌ Cannot connect to database")
        return
    
    try:
        # Analyze recent changes
        recent_sales, movements = analyze_recent_stock_changes(conn)
        
        # Check for bug patterns
        check_stock_calculation_bug(conn)
        
        # Analyze business logic
        analyze_business_logic()
        
        # Check data type issues
        check_for_data_type_issues(conn)
        
        # Create test scenario
        create_test_scenario(conn)
        
        print(f"\n" + "=" * 70)
        print(f"📋 BUG INVESTIGATION SUMMARY")
        print(f"=" * 70)
        
        print(f"\n🔍 Most Likely Causes:")
        print(f"1. Race condition - Multiple sales processing simultaneously")
        print(f"2. Stock calculation error in business logic")
        print(f"3. Database transaction issues")
        print(f"4. Data type precision problems")
        print(f"5. Stock movement logging errors")
        
        print(f"\n🔧 Recommended Fixes:")
        print(f"1. Add stock validation before and after each sale")
        print(f"2. Implement proper database transactions")
        print(f"3. Add logging for stock changes")
        print(f"4. Check for concurrent sale processing")
        print(f"5. Verify data type handling")
        
        # Save investigation report
        report_file = f"stock_bug_investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"Stock Bug Investigation Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Recent sales analyzed: {len(recent_sales)}\n")
            f.write(f"Stock movements analyzed: {len(movements)}\n")
        
        print(f"\n📄 Investigation report saved to: {report_file}")
        
    finally:
        conn.close()
        print(f"\n✅ Investigation completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
