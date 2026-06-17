#!/usr/bin/env python3
"""
Check which stock columns exist in the database and which one the application uses
"""

import os
import sys
import psycopg2
import json

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

def check_stock_columns():
    """Check which stock columns exist in products table"""
    print("=" * 60)
    print("🔍 CHECKING STOCK COLUMNS IN PRODUCTS TABLE")
    print("=" * 60)
    
    conn = connect_to_postgres()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all columns from products table
        cursor.execute("""
            SELECT column_name, data_type, numeric_precision, numeric_scale, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'products' AND table_schema = 'public'
            AND (column_name ILIKE '%stock%' OR column_name ILIKE '%quantity%' OR column_name ILIKE '%level%')
            ORDER BY ordinal_position
        """)
        
        stock_columns = cursor.fetchall()
        
        print(f"📋 Stock-related columns found:")
        for col in stock_columns:
            col_name, data_type, precision, scale, nullable, default = col
            print(f"  • {col_name}: {data_type}")
            if precision:
                print(f"    Precision: {precision}, Scale: {scale}")
            if default:
                print(f"    Default: {default}")
            print(f"    Nullable: {nullable}")
            print()
        
        if not stock_columns:
            print("❌ No stock-related columns found!")
            return
        
        # Check DUMY PRODUCT specifically
        print("🔍 CHECKING DUMY PRODUCT STOCK VALUES:")
        cursor.execute("""
            SELECT id, name
            FROM products 
            WHERE name ILIKE '%DUMY%' OR name ILIKE '%dummy%'
            ORDER BY id
            LIMIT 5
        """)
        
        dummy_products = cursor.fetchall()
        
        if not dummy_products:
            print("❌ No DUMY products found")
            return
        
        for product in dummy_products:
            prod_id, name = product
            print(f"\n📊 Product: {name} (ID: {prod_id})")
            
            # Get all stock-related values for this product
            stock_values = {}
            for col in stock_columns:
                col_name = col[0]
                try:
                    cursor.execute(f"SELECT {col_name} FROM products WHERE id = {prod_id}")
                    value = cursor.fetchone()[0]
                    stock_values[col_name] = value
                except Exception as e:
                    stock_values[col_name] = f"ERROR: {e}"
            
            print("  Stock values:")
            for col_name, value in stock_values.items():
                print(f"    {col_name}: {value}")
        
        # Check which column is actually used in sales logic
        print(f"\n🔍 CHECKING WHICH STOCK COLUMN IS USED:")
        
        # Look at recent sales to see which stock column changes
        cursor.execute("""
            SELECT 
                si.product_id,
                p.name,
                p.stock_level,
                p.warehouse_stock,
                p.retail_stock,
                si.created_at
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE p.name ILIKE '%DUMY%' OR p.name ILIKE '%dummy%'
            ORDER BY si.created_at DESC
            LIMIT 10
        """)
        
        try:
            recent_sales = cursor.fetchall()
            print("  Recent sales data:")
            for sale in recent_sales:
                prod_id, name, stock_level, warehouse_stock, retail_stock = sale
                print(f"    {name} (ID: {prod_id})")
                print(f"      stock_level: {stock_level}")
                print(f"      warehouse_stock: {warehouse_stock}")
                print(f"      retail_stock: {retail_stock}")
        except Exception as e:
            print(f"  Could not check recent sales: {e}")
        
        # Check if there are any triggers or constraints on stock columns
        print(f"\n🔍 CHECKING FOR STOCK TRIGGERS:")
        cursor.execute("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'products'
            AND action_statement ILIKE '%stock%'
        """)
        
        triggers = cursor.fetchall()
        if triggers:
            print("  Stock-related triggers found:")
            for trigger in triggers:
                trigger_name, event, action = trigger
                print(f"    {trigger_name}: {event}")
                print(f"      Action: {action[:100]}...")
        else:
            print("  No stock-related triggers found")
        
    except Exception as e:
        print(f"❌ Error checking stock columns: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def main():
    check_stock_columns()

if __name__ == "__main__":
    main()
