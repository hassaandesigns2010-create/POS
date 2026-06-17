#!/usr/bin/env python3
"""
Investigate the REAL cause of stock going to zero without modifying anything
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

def analyze_stock_movement_pattern():
    """Look for patterns in stock movements that might reveal the bug"""
    print("=== STOCK MOVEMENT PATTERN ANALYSIS ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check if stock_movements table exists and what it contains
        try:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'stock_movements' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"📋 Stock movements table columns:")
            for col in columns:
                print(f"  • {col[0]}: {col[1]}")
            
            # Get recent stock movements
            cursor.execute("""
                SELECT COUNT(*) as total_movements
                FROM stock_movements
            """)
            
            total_movements = cursor.fetchone()[0]
            print(f"\n📊 Total stock movements: {total_movements}")
            
            if total_movements > 0:
                # Get recent movements with product details
                cursor.execute("""
                    SELECT 
                        sm.id,
                        sm.product_id,
                        p.name as product_name,
                        p.stock_level as current_stock,
                        sm.movement_type,
                        sm.quantity,
                        sm.reference_type,
                        sm.reference_id,
                        sm.created_at
                    FROM stock_movements sm
                    JOIN products p ON sm.product_id = p.id
                    ORDER BY sm.created_at DESC
                    LIMIT 20
                """)
                
                movements = cursor.fetchall()
                print(f"\n📦 Recent stock movements:")
                
                for movement in movements:
                    mov_id, product_id, product_name, current_stock, mov_type, qty, ref_type, ref_id, mov_time = movement
                    print(f"  {mov_time} | {product_name[:30]:30s}")
                    print(f"    Type: {mov_type} | Qty: {qty} | Ref: {ref_type}#{ref_id}")
                    print(f"    Current Stock: {current_stock}")
                    print()
            
        except Exception as e:
            print(f"❌ Error analyzing stock movements: {e}")
        
    finally:
        conn.close()

def check_for_zero_stock_patterns():
    """Look for patterns that might cause stock to become zero"""
    print("\n=== ZERO STOCK PATTERN ANALYSIS ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Find products that recently went to zero stock
        cursor.execute("""
            SELECT 
                id, name, stock_level, barcode, retail_price
            FROM products 
            WHERE stock_level = 0
            ORDER BY name
            LIMIT 15
        """)
        
        zero_stock_products = cursor.fetchall()
        print(f"🔍 Products with zero stock:")
        
        suspicious_patterns = []
        
        for product in zero_stock_products:
            prod_id, name, stock, barcode, price = product
            print(f"  ID:{prod_id:4d} | {name[:40]:40s} | {barcode:12s} | Price:{price:8.2f}")
            
            # Check if this product was recently sold
            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as sale_count,
                        SUM(quantity) as total_sold,
                        MAX(si.created_at) as last_sale
                    FROM sale_items si
                    WHERE si.product_id = {prod_id}
                """)
                
                sale_data = cursor.fetchone()
                sale_count, total_sold, last_sale = sale_data
                
                if sale_count > 0:
                    print(f"    📊 Sold {total_sold} units in {sale_count} sales")
                    print(f"    📅 Last sale: {last_sale}")
                    
                    # Check if this looks suspicious
                    if total_sold > 0 and stock == 0:
                        suspicious_patterns.append({
                            'product_id': prod_id,
                            'name': name,
                            'total_sold': total_sold,
                            'sale_count': sale_count,
                            'last_sale': last_sale
                        })
                
            except Exception as e:
                print(f"    ❓ Could not check sales data: {e}")
        
        # Analyze suspicious patterns
        if suspicious_patterns:
            print(f"\n⚠️  Found {len(suspicious_patterns)} suspicious patterns:")
            for pattern in suspicious_patterns:
                print(f"  Product: {pattern['name'][:40]:40s}")
                print(f"    Sold: {pattern['total_sold']} units in {pattern['sale_count']} sales")
                print(f"    Last sale: {pattern['last_sale']}")
                print()
        
    except Exception as e:
        print(f"❌ Error checking zero stock patterns: {e}")
    finally:
        conn.close()

def analyze_sale_item_quantities():
    """Analyze sale item quantities for anomalies"""
    print("\n=== SALE ITEM QUANTITY ANALYSIS ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Look for unusual quantities in sale items
        cursor.execute("""
            SELECT 
                product_id,
                COUNT(*) as sale_count,
                SUM(quantity) as total_quantity,
                AVG(quantity) as avg_quantity,
                MAX(quantity) as max_quantity,
                MIN(quantity) as min_quantity
            FROM sale_items
            GROUP BY product_id
            HAVING COUNT(*) > 1
            ORDER BY total_quantity DESC
            LIMIT 10
        """)
        
        quantity_patterns = cursor.fetchall()
        print(f"📊 Products with multiple sales (top 10 by total quantity):")
        
        for pattern in quantity_patterns:
            product_id, sale_count, total_qty, avg_qty, max_qty, min_qty = pattern
            
            # Get product name
            try:
                cursor.execute(f"SELECT name FROM products WHERE id = {product_id}")
                product_name = cursor.fetchone()[0]
            except:
                product_name = "Unknown"
            
            print(f"  {product_name[:35]:35s} (ID:{product_id})")
            print(f"    Sales: {sale_count} | Total: {total_qty:.1f} | Avg: {avg_qty:.1f}")
            print(f"    Range: {min_qty:.1f} - {max_qty:.1f}")
            
            # Look for suspicious patterns
            if max_qty > 10:
                print(f"    ⚠️  High quantity sale detected!")
            if avg_qty > 5:
                print(f"    ⚠️  High average quantity!")
            print()
        
        # Look for very large single sales
        cursor.execute("""
            SELECT 
                si.product_id,
                p.name as product_name,
                si.quantity,
                si.unit_price,
                si.created_at
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.quantity > 10
            ORDER BY si.quantity DESC
            LIMIT 10
        """)
        
        large_sales = cursor.fetchall()
        if large_sales:
            print(f"🚨 Large quantity sales (>10 units):")
            for sale in large_sales:
                product_id, product_name, quantity, unit_price, sale_time = sale
                print(f"  {product_name[:35]:35s}")
                print(f"    Quantity: {quantity:.1f} | Price: {unit_price:.2f} | Time: {sale_time}")
        
    except Exception as e:
        print(f"❌ Error analyzing sale quantities: {e}")
    finally:
        conn.close()

def check_for_decimal_precision_issues():
    """Check for decimal precision issues that might cause stock problems"""
    print("\n=== DECIMAL PRECISION ANALYSIS ===")
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check stock_level precision in database
        cursor.execute("""
            SELECT 
                stock_level,
                COUNT(*) as count
            FROM products 
            WHERE stock_level > 0 AND stock_level < 1
            GROUP BY stock_level
            ORDER BY stock_level
        """)
        
        fractional_stocks = cursor.fetchall()
        if fractional_stocks:
            print(f"🔍 Products with fractional stock (0 < stock < 1):")
            for stock_val, count in fractional_stocks:
                print(f"  Stock: {stock_val} | Count: {count}")
        else:
            print(f"✅ No fractional stock values found")
        
        # Check for very small stock values that might indicate precision issues
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM products 
            WHERE stock_level > 0 AND stock_level < 0.01
        """)
        
        tiny_stocks = cursor.fetchone()[0]
        if tiny_stocks > 0:
            print(f"⚠️  Found {tiny_stocks} products with very small stock (< 0.01)")
        
        # Check sale item quantities for precision issues
        cursor.execute("""
            SELECT 
                quantity,
                COUNT(*) as count
            FROM sale_items
            WHERE quantity > 0 AND quantity < 1
            GROUP BY quantity
            ORDER BY quantity
        """)
        
        fractional_quantities = cursor.fetchall()
        if fractional_quantities:
            print(f"\n🔍 Fractional sale quantities:")
            for qty, count in fractional_quantities:
                print(f"  Quantity: {qty} | Count: {count}")
        
    except Exception as e:
        print(f"❌ Error checking decimal precision: {e}")
    finally:
        conn.close()

def main():
    print("=" * 70)
    print("🔍 INVESTIGATING REAL STOCK BUG CAUSE")
    print("=" * 70)
    print("Issue: Stock goes to zero without proper reason")
    print("NOTE: This investigation does NOT modify any data")
    print(f"Started at: {datetime.now()}")
    
    # Analyze stock movement patterns
    analyze_stock_movement_pattern()
    
    # Check for zero stock patterns
    check_for_zero_stock_patterns()
    
    # Analyze sale item quantities
    analyze_sale_item_quantities()
    
    # Check for decimal precision issues
    check_for_decimal_precision_issues()
    
    print(f"\n" + "=" * 70)
    print("📋 INVESTIGATION SUMMARY")
    print("=" * 70)
    
    print("\n🎯 Possible Real Causes:")
    print("1. **Stock movement calculation error** - Wrong quantity calculations")
    print("2. **Sale item quantity error** - Wrong quantities being recorded")
    print("3. **Decimal precision issue** - Rounding or precision errors")
    print("4. **Stock movement logging error** - Stock updated but movement recorded wrong")
    print("5. **Database trigger issue** - Trigger modifying stock incorrectly")
    print("6. **Application-level bug** - UI sending wrong quantities")
    
    print("\n🔧 Next Steps (without modifying stock):")
    print("1. Check recent sale logs for unusual quantities")
    print("2. Verify stock movement records match actual changes")
    print("3. Look for database triggers that might affect stock")
    print("4. Check application logs for stock-related errors")
    print("5. Monitor a test sale to see exactly what happens")
    
    print(f"\n✅ Investigation completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
