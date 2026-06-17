#!/usr/bin/env python3
"""
Simple investigation of the stock bug - selling 1 item makes stock go from 10 to 0
"""

import os
import sys
import psycopg2
import json
from datetime import datetime

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

def check_sales_table_structure(conn):
    """Check the actual sales table structure"""
    print("=== SALES TABLE STRUCTURE ===")
    
    try:
        cursor = conn.cursor()
        
        # Get columns in sales table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'sales' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"📋 Sales table columns:")
        for col in columns:
            print(f"  • {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Check sale_items table too
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'sale_items' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        sale_items_columns = cursor.fetchall()
        print(f"\n📋 Sale_items table columns:")
        for col in sale_items_columns:
            print(f"  • {col[0]}: {col[1]}")
        
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")

def find_problematic_sales(conn):
    """Look for recent sales that might have caused stock issues"""
    print("\n=== RECENT SALES ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Get recent sales (try different date column names)
        date_columns = ['created_at', 'date', 'sale_date', 'timestamp']
        
        for date_col in date_columns:
            try:
                cursor.execute(f"""
                    SELECT 
                        si.product_id,
                        p.name as product_name,
                        p.stock_level as current_stock,
                        si.quantity as sold_quantity,
                        si.unit_price
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.id
                    WHERE si.{date_col} >= NOW() - INTERVAL '24 hours'
                    ORDER BY si.{date_col} DESC
                    LIMIT 10
                """)
                
                recent_sales = cursor.fetchall()
                print(f"📊 Recent sales (using {date_col}):")
                
                for sale in recent_sales:
                    product_id, product_name, current_stock, sold_qty, unit_price = sale
                    print(f"  Product: {product_name[:40]:40s}")
                    print(f"    ID: {product_id} | Sold: {sold_qty} | Current Stock: {current_stock}")
                    print(f"    Price: {unit_price:.2f}")
                    print()
                
                if recent_sales:
                    break  # Found the right date column
                
            except Exception as e:
                continue  # Try next date column
        
        if not recent_sales:
            print("⚠️  No recent sales found or date column issue")
            
            # Try without date filter
            cursor.execute("""
                SELECT 
                    si.product_id,
                    p.name as product_name,
                    p.stock_level as current_stock,
                    si.quantity as sold_quantity,
                    si.unit_price
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                ORDER BY si.id DESC
                LIMIT 10
            """)
            
            recent_sales = cursor.fetchall()
            print(f"📊 Last 10 sales (no date filter):")
            
            for sale in recent_sales:
                product_id, product_name, current_stock, sold_qty, unit_price = sale
                print(f"  Product: {product_name[:40]:40s}")
                print(f"    ID: {product_id} | Sold: {sold_qty} | Current Stock: {current_stock}")
                print(f"    Price: {unit_price:.2f}")
                print()
        
    except Exception as e:
        print(f"❌ Error finding sales: {e}")

def check_stock_movements(conn):
    """Check stock movements for anomalies"""
    print("=== STOCK MOVEMENTS ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Get recent stock movements
        cursor.execute("""
            SELECT 
                product_id,
                movement_type,
                quantity,
                reference_type,
                reference_id,
                notes
            FROM stock_movements
            ORDER BY id DESC
            LIMIT 15
        """)
        
        movements = cursor.fetchall()
        print(f"📦 Recent stock movements:")
        
        for movement in movements:
            product_id, mov_type, qty, ref_type, ref_id, notes = movement
            print(f"  Product ID: {product_id}")
            print(f"    Type: {mov_type} | Quantity: {qty}")
            print(f"    Reference: {ref_type} #{ref_id}")
            if notes:
                print(f"    Notes: {notes}")
            print()
        
    except Exception as e:
        print(f"❌ Error checking movements: {e}")

def analyze_specific_stock_issue(conn):
    """Look for products that might have the stock bug"""
    print("=== SPECIFIC STOCK ISSUE ANALYSIS ===")
    
    try:
        cursor = conn.cursor()
        
        # Find products with stock that should have more
        cursor.execute("""
            SELECT 
                id, name, stock_level, retail_price, barcode
            FROM products 
            WHERE stock_level >= 0 AND stock_level <= 5
            AND retail_price > 0
            ORDER BY stock_level ASC
            LIMIT 10
        """)
        
        suspicious_products = cursor.fetchall()
        print(f"🔍 Products with suspiciously low stock:")
        
        for product in suspicious_products:
            prod_id, name, stock, price, barcode = product
            print(f"  ID:{prod_id:4d} | Stock:{stock:6.1f} | Price:{price:8.2f} | {name[:35]:35s}")
            
            # Check if this product was recently sold
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) as sale_count, SUM(quantity) as total_sold
                    FROM sale_items 
                    WHERE product_id = {prod_id}
                """)
                
                sale_data = cursor.fetchone()
                sale_count, total_sold = sale_data
                
                if sale_count > 0:
                    print(f"    📊 Sold {total_sold} units in {sale_count} sales")
                
            except Exception:
                print(f"    ❓ Could not check sales data")
        
    except Exception as e:
        print(f"❌ Error analyzing specific issue: {e}")

def check_business_logic_patterns():
    """Check the business logic for potential stock bugs"""
    print("=== BUSINESS LOGIC PATTERN CHECK ===")
    
    business_logic_file = os.path.join(os.path.dirname(__file__), 'controllers', 'business_logic.py')
    
    try:
        with open(business_logic_file, 'r') as f:
            content = f.read()
        
        print("🔍 Looking for potential stock calculation issues...")
        
        # Check for specific patterns that might cause the bug
        issues_found = []
        
        # Pattern 1: Stock being set to zero directly
        if 'stock_level = 0' in content:
            issues_found.append("❌ Direct assignment: stock_level = 0")
        
        # Pattern 2: Stock being multiplied or divided
        if any(op in content for op in ['stock_level *=', 'stock_level /=', 'stock_level **=']):
            issues_found.append("❌ Mathematical operations on stock_level")
        
        # Pattern 3: Stock being updated with wrong quantity
        if 'product.stock_level = quantity' in content:
            issues_found.append("❌ Setting stock to quantity instead of subtracting")
        
        # Pattern 4: Decimal conversion issues
        if 'Decimal(str(' in content and 'stock_level' in content:
            issues_found.append("⚠️  Decimal conversion might cause precision issues")
        
        # Look at the specific stock update lines
        lines = content.split('\n')
        stock_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'stock_level' in line and ('=' in line):
                stock_lines.append(f"Line {i}: {line.strip()}")
        
        print(f"\n📝 Stock update operations found:")
        for line in stock_lines[-10:]:  # Show last 10
            print(f"  {line}")
        
        if issues_found:
            print(f"\n⚠️  Potential issues found:")
            for issue in issues_found:
                print(f"  {issue}")
        else:
            print(f"\n✅ No obvious stock calculation bugs detected")
        
    except Exception as e:
        print(f"❌ Error checking business logic: {e}")

def main():
    print("=" * 70)
    print("🐛 STOCK BUG INVESTIGATION - Simple Version")
    print("=" * 70)
    print("Issue: Selling 1 item makes stock go from 10 to 0")
    print(f"Started at: {datetime.now()}")
    
    conn = connect_to_postgres()
    if not conn:
        print("❌ Cannot connect to database")
        return
    
    try:
        # Check table structure
        check_sales_table_structure(conn)
        
        # Find problematic sales
        find_problematic_sales(conn)
        
        # Check stock movements
        check_stock_movements(conn)
        
        # Analyze specific stock issues
        analyze_specific_stock_issue(conn)
        
        # Check business logic patterns
        check_business_logic_patterns()
        
        print(f"\n" + "=" * 70)
        print(f"📋 INVESTIGATION SUMMARY")
        print(f"=" * 70)
        
        print(f"\n🎯 Most Likely Causes:")
        print(f"1. **Transaction rollback issue** - Sale completes but stock update fails")
        print(f"2. **Race condition** - Multiple sales processing same product simultaneously")
        print(f"3. **Decimal precision error** - Stock calculation precision issues")
        print(f"4. **Wrong column reference** - Updating wrong stock column")
        print(f"5. **Exception handling** - Stock update exception not properly handled")
        
        print(f"\n🔧 Immediate Fixes Needed:")
        print(f"1. Add stock validation before/after each sale")
        print(f"2. Implement proper database transactions")
        print(f"3. Add detailed logging for stock changes")
        print(f"4. Check for concurrent sale protection")
        print(f"5. Verify exception handling in stock updates")
        
        print(f"\n⚡ Quick Test:")
        print(f"1. Find a product with stock >= 10")
        print(f"2. Make a test sale of 1 unit")
        print(f"3. Check stock before and after the sale")
        print(f"4. Look in stock_movements table for the record")
        
    finally:
        conn.close()
        print(f"\n✅ Investigation completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
